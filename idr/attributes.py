"""
Helper functions for accessing the IDR from within IPython notebooks.
"""
import pandas
import omero.clients # NOQA
from omero.rtypes import rlist, rstring, unwrap
from omero.sys import ParametersI
from externalDBs import get_entrezid, get_ensembleid, ensembleid_to_genesymbol

from widgets import progress
import numpy as np


def attributes_by_attributes(conn,
                             name="Gene Symbol",
                             value="ASH2L",
                             ns="openmicroscopy.org/mapr/gene",
                             ns2="openmicroscopy.org/mapr/phenotype",
                             name2=None,
                             s_id=None
                             ):

    """
    Return a list of neighbours attributes
    for given case insensitive attribute value. (Uses the python blitz gateway)
    """
    params = ParametersI()
    params.addString("value", value.lower())
    q = (
        "select distinct new map( mv.value as value) "
        "from Annotation as a "
        "join a.mapValue as mv "
        "where lower(mv.value) = :value {where_claus}"
    )
    where_claus = []
    if name:
        params.addString("name", name)
        where_claus.append("and mv.name = :name")
    q = q.format(**{'where_claus': " ".join(where_claus)})

    values = [v[0]['value'] for v in unwrap(
        conn.getQueryService().projection(q, params))]

    params = ParametersI()
    valuelist = [rstring(unicode(v)) for v in values]
    params.add('values', rlist(valuelist))
    params.addString("ns", ns)
    params.addString("ns2", ns2)

    q = (
        "select distinct new map("
        "mv.name as name, "
        "mv.value as value, "
        "mv2.name as name2, "
        "mv2.value as value2) "
        "from Image as i "
        "join i.annotationLinks as ial "
        "join i.annotationLinks as ial2 "
        "join ial.child as a "
        "join a.mapValue as mv "
        "join ial2.child as a2 "
        "join a2.mapValue as mv2 "
        "where a.ns = :ns and a2.ns = :ns2 "
        "and mv.value in (:values) {where_claus} "
    )

    where_claus = []
    if name:
        params.addString("name", name)
        where_claus.append("and mv.name = :name")
    if name2:
        params.addString("name2", name2)
        where_claus.append("and mv2.name = :name2")

    q = q.format(**{'where_claus': " ".join(where_claus)})

    if s_id is not None:
        q = q + ("and i in (select image from WellSample "
                 "where well.plate in "
                 "(select child from ScreenPlateLink where "
                 "parent.id = {sId}))")

        screen_id_list = []
        screen_id_list.append(str(s_id))
        q = q.format(**{'sId': " ".join(screen_id_list)})

    res = {}
    for r in unwrap(conn.getQueryService().projection(q, params)):
        r = r[0]
        try:
            res[(r['name'], r['value'])].append((r['name2'], r['value2']))
        except KeyError:
            res[(r['name'], r['value'])] = [(r['name2'], r['value2'])]
    return res


def annotation_ids_by_field(conn,
                            value="CMPO_0000077",
                            key="Phenotype Term Accession",
                            ns="openmicroscopy.org/mapr/phenotype"):
    """
    Return a list of IDs for map annotations with the given namespace
    that have a key=value pair matching the given parameters.
    """

    params = ParametersI()
    params.addString("value", value)
    params.addString("key", key)
    params.addString("ns", ns)
    q = ("select a.id from MapAnnotation a join a.mapValue as mv "
         "where a.ns = :ns and mv.name = :key and mv.value = :value")

    return unwrap(conn.getQueryService().projection(q, params))[0]


def get_phenotypes_for_gene(session,
                            gene_name,
                            screenid=None,
                            idr_base_url="https://idr.openmicroscopy.org"):

    """
    Return a list of phenotype
    for given case insensitive gene_name. (Uses the json api)
    """

    v = "{base}/mapr/api/{key}/"
    screens_projects_url = v + "?value={value}"
    plates_url = v + "plates/?value={value}&id={screen_id}"
    images_url = v + "images/?value={value}&node={parent_type}&id={parent_id}"
    map_url = "{base}/webclient/api/annotations/?type=map&{type}={image_id}"

    screen_id_list = []
    if screenid is not None:
        screen_id_list.append(screenid)
    else:
        qs = {'base': idr_base_url, 'key': 'gene', 'value': gene_name}
        url = screens_projects_url.format(**qs)
        for s in session.get(url).json()['screens']:
            screen_id_list.append(s['id'])

    unique_list = []
    unique_list_1 = []
    unique_list_2 = []

    if len(screen_id_list) == 0:
        phenotype_ids_dataframe = pandas.DataFrame(
            {'Name': unique_list,
             'Accession': unique_list_1,
             'phenotypeAndScreenId': unique_list_1})
        return phenotype_ids_dataframe

    for sid in screen_id_list:
        screen_id = sid
        screenqs = {'base': idr_base_url, 'key': 'gene',
                    'value': gene_name, 'screen_id': screen_id}
        screenurl = plates_url.format(**screenqs)
        phenotype_per_screen = []
        phenotype_id_per_screen = []
        screen_ids = []
        t_name = 'Phenotype Term Name'
        t_access = 'Phenotype Term Accession'
        for p in session.get(screenurl).json()['plates']:
            plate_id = p['id']
            imageqs = {'base': idr_base_url, 'key': 'gene',
                       'value': gene_name, 'parent_type': 'plate',
                       'parent_id': plate_id}
            plateurl = images_url.format(**imageqs)
            for i in session.get(plateurl).json()['images']:
                image_id = i['id']
                qs = {'base': idr_base_url,
                      'type': 'image',
                      'image_id': image_id}
                url = map_url.format(**qs)
                for a in session.get(url).json()['annotations']:
                    for v in a['values']:
                        key = v[0]
                        value = v[1]
                        if key.startswith(t_name) & key.endswith(t_name):
                            phenotype_per_screen.append(value)
                            screen_ids.append(str(screen_id) + '_' + value)
                        if key.startswith(t_access) & key.endswith(t_access):
                            phenotype_id_per_screen.append(value)

        unique_list = unique_list + list(set(phenotype_per_screen))
        unique_list_1 = unique_list_1 + list(set(phenotype_id_per_screen))
        unique_list_2 = unique_list_2 + list(set(screen_ids))

        phenotype_ids_dataframe = pandas.DataFrame(
            {'Name': unique_list,
             'Accession': unique_list_1,
             'phenotypeAndScreenId': unique_list_2})

    return phenotype_ids_dataframe


def get_phenotypes_for_genelist(session,
                                go_gene_list,
                                organism,
                                idr_base_url="https://idr.openmicroscopy.org",
                                lookup_entrez=True):

    """
    Return a list of phenotypes (dataframe)
    for given case insensitive gene_list. (Uses the json api)
    """

    genedict = {}
    totalphenotypename = []
    totalphenotypeaccession = []
    totalscreenids = []
    testedgenes = []

    phenotypenametoacc = {}
    for ids, gene in enumerate(go_gene_list):

        if gene.startswith("-"):
            continue

        if lookup_entrez:
            entrezid = get_entrezid(gene)
        else:
            entrezid = '-'
        ensembleid = get_ensembleid(gene)

        gid = None
        # search with the gene name
        uniquelist = []
        if len(uniquelist) == 0:
            key = "GeneName"
            gid = gene
            uniquelist = get_phenotypes_for_gene(session,
                                                 gid)

        # search with ensembleid if geneSymbol does not
        # return any result
        if len(uniquelist['Name']) == 0:
            key = "EnsemblID"
            for gid in ensembleid:
                uniquelist = get_phenotypes_for_gene(session,
                                                     gid)
                if len(uniquelist['Name']) != 0:
                    break

        # search with entrezid if gene symbol and
        # ensembleid does not return any result
        if lookup_entrez:
            if len(uniquelist) == 0:
                key = "EntrezID"
                for gid in entrezid:
                    uniquelist = get_phenotypes_for_gene(session,
                                                         gid)
                    if len(uniquelist['Name']) != 0:
                        break

        # List of genes from string which were part of IDR
        if gid is not None:
            testedgenes.append(gid)

        # Dataframe of genes from string which were part of IDR
        # and had a phenotype associated with them
        if len(uniquelist) != 0:

            accname = uniquelist['Name']
            accid = uniquelist['Accession']
            scrid = uniquelist['phenotypeAndScreenId']

            accnames = list(accname.values)
            accids = list(accid.values)
            idlist = []
            for id in scrid:
                idx = id.index('_')
                idlist.append(id[:idx])

            for idx, idx1 in enumerate(accnames):
                phenotypenametoacc[accnames[idx]] = accids[idx]

            totalphenotypename = totalphenotypename + accnames
            totalphenotypeaccession = totalphenotypeaccession + accids
            totalscreenids = totalscreenids + list(scrid.values)

            genedict[gene] = [entrezid, ensembleid,
                              None, None, None, None, None]
            genedict[gene][2] = key
            genedict[gene][3] = gid
            genedict[gene][4] = accnames
            genedict[gene][5] = accids
            genedict[gene][6] = idlist

        progress(ids+1, len(go_gene_list),
                 status='Iterating through gene list')

    query_genes_dataframe = pandas.DataFrame.from_dict(genedict,
                                                       orient='index')
    query_genes_dataframe.columns = ("Entrez", "Ensembl",
                                     "Key", "Value", "PhenotypeName",
                                     "PhenotypeAccession", "ScreenIds")

    # get the screens to phenotypes map for the query genes
    organism_screen_idlist = get_organism_screenids(session, organism)
    genes_scid_list = [item for sublist in
                       query_genes_dataframe['ScreenIds'].values
                       for item in sublist]
    genes_scid_list = list(set(genes_scid_list))
    screen_to_phenotype_dictionary = {}
    for scid in genes_scid_list:
        if scid in organism_screen_idlist:
            content = [x for x in set(list(totalscreenids))
                       if x.startswith(scid)]
            for idx, item in enumerate(content):
                idx1 = item.index('_')
                content[idx] = item[idx1+1:]
            screen_to_phenotype_dictionary[scid] = content

    return [query_genes_dataframe, screen_to_phenotype_dictionary]


def get_similar_genes(conn, query_genes_list, screen_to_phenotype_dictionary):

    """
    Return a multi-dimensional dictionary with the
    following mapping,
    similar_genes[screenid][phenotypename] = similar_genes_list
    (uses python blitz gateway)
    """

    similar_genes = {}
    overlap_genes = {}
    scid_list = set(list(screen_to_phenotype_dictionary.keys()))
    for i, sid in enumerate(set(scid_list)):

        phlist = screen_to_phenotype_dictionary[sid]
        similar_genes[str(sid)] = {}
        overlap_genes[str(sid)] = {}
        for phenotype in np.unique(phlist):

            args = {
                "name": "Phenotype Term Name",
                "value": phenotype,
                "ns": "openmicroscopy.org/mapr/phenotype",
                "ns2": "openmicroscopy.org/mapr/gene",
                "s_id": sid
            }

            cc = attributes_by_attributes(conn, **args)
            dataframe = pandas.DataFrame.from_dict(cc)

            if dataframe.empty:
                continue

            gene_list = []
            for x in dataframe.iloc[:, 0]:

                key = x[0]
                value = x[1]

                if key == "Gene Identifier" and value.startswith("EN"):
                    id = value
                    gene_list.append(id)
                if key == "Gene Symbol":
                    genesym = value
                    gene_list.append(genesym)

            ov_genes = set(gene_list).intersection(query_genes_list)

            remove_duplicates = []
            removed_genes = []
            for g in ov_genes:
                converted = g
                if g.startswith('ENSG'):
                    converted = ensembleid_to_genesymbol(g)
                    removed_genes.append(g)
                remove_duplicates.append(converted)

            ov_genes = set(remove_duplicates)

            if len(ov_genes) != 0:
                setdiff_genes = set(gene_list) - ov_genes - set(removed_genes)
                similar_genes[str(sid)][phenotype] = list(setdiff_genes)
                overlap_genes[str(sid)][phenotype] = list(ov_genes)

        progress(i+1, len(set(scid_list)), status='Iterating through screens')

    return [similar_genes, overlap_genes]


def get_organism_screenids(session, organism,
                           idr_base_url="https://idr.openmicroscopy.org"):

    """
    Return a list of screen ids in IDR
    for given case insensitive organism. (Uses the json api)
    """

    screen_id_list = []
    qs = {'base': idr_base_url, 'key': 'organism', 'value': organism}
    screens_projects_url = "{base}/mapr/api/{key}/?value={value}"
    url = screens_projects_url.format(**qs)
    for s in session.get(url).json()['screens']:
        screen_id_list.append(str(s['id']))

    return screen_id_list
