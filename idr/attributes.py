"""
Helper functions for accessing the IDR from within IPython notebooks.
"""
import pandas
from omero.rtypes import rlist, rstring, unwrap
from omero.sys import ParametersI


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


def get_phenotypes_for_gene(idr_base_url, session, gene_name, screenid=None):

    """
    Return a list of phenotype
    for given case insensitive gene_name. (Uses the json api and python blitz gateway)
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
                        if key.startswith(t_access) & key.endswith(t_access):
                            phenotype_id_per_screen.append(value)

        unique_list = unique_list + list(set(phenotype_per_screen))
        unique_list_1 = unique_list_1 + list(set(phenotype_id_per_screen))
        unique_list_2 = [screen_id] * len(unique_list)

        phenotype_ids_dataframe = pandas.DataFrame(
            {'Name': unique_list,
             'Accession': unique_list_1,
             'phenotypeAndScreenId': unique_list_2})

    return phenotype_ids_dataframe

def get_phenotypes_for_genelist(idr_base_url, session, go_gene_list):
    
    """
    Return a list of phenotypes (dataframe)
    for given case insensitive gene_list. (Uses the json api and python blitz gateway)
    """

    f = FloatProgress(min=0, max=len(go_gene_list)))
    display(f)

    df = {}
    totalPhenotypeName = []
    totalPhenotypeAccession = []
    totalScreenIds = []
    testedgenes = []

    phenotypeNameToAcc = {}
    for gene in go_gene_list:

        if gene.startswith("-"):
            continue
        entrezid = get_entrezid(gene)
        ensembleid = get_ensembleid(gene)
        f.value += 1 
        gid = None
        # search with the gene name
        uniqueList = []
        if len(uniqueList) == 0:
            key = "GeneName"
            gid = gene
            uniqueList = get_phenotypes_for_gene(idr_base_url, session, gid)

        # search with ensembleid if geneSymbol does not return any result
        if len(uniqueList['Name']) == 0:
            key = "EnsemblID"
            for gid in ensembleid:
                uniqueList = get_phenotypes_for_gene(idr_base_url, session, gid)
                if len(uniqueList['Name']) != 0:
                    break

        # search with entrezid if gene symbol and ensembleid does not return any result 
        if len(uniqueList) == 0:
            key = "EntrezID"
            for gid in entrezid:
                uniqueList = get_phenotypes_for_gene(idr_base_url, session, gid)
                if len(uniqueList['Name']) != 0:
                    break

        # List of genes from string which were part of IDR
        if gid != None:
            testedgenes.append(gid)

        # Dataframe of genes from string which were part of IDR and had a phenotype associated with them
        if len(uniqueList) != 0:

            accname = uniqueList['Name']
            accid = uniqueList['Accession']
            scrid = uniqueList['phenotypeAndScreenId']

            accnames = list(accname.values)
            accids = list(accid.values)
            idlist = []
            for id in scrid:
                idx = id.index('_')
                idlist.append(id[:idx])

            for idx,idx1 in enumerate(accnames):
                phenotypeNameToAcc[accnames[idx]] = accids[idx]     

            totalPhenotypeName = totalPhenotypeName + accnames
            totalPhenotypeAccession = totalPhenotypeAccession + accids
            totalScreenIds = totalScreenIds + list(scrid.values)

            df[gene] = [entrezid, ensembleid, None, None, None, None,None]
            df[gene][2] = key
            df[gene][3] = gid
            df[gene][4] = accnames
            df[gene][5] = accids
            df[gene][6] = idlist

    genes = pandas.DataFrame.from_dict(df, orient='index')
    genes.columns = ("Entrez", "Ensembl", "Key", "Value", "PhenotypeName", "PhenotypeAccession","ScreenIds")
    totalphenotypelist = {}
    totalphenotypelist['totalPhenotypeName'] = totalPhenotypeName
    totalphenotypelist['totalPhenotypeAccession'] = totalPhenotypeAccession
    totalphenotypelist['totalScreenIds'] = totalScreenIds
    total_lists = pandas.DataFrame.from_dict(totalphenotypelist, orient='index')
    
    return [genes,total_lists]


def get_organism_screenids(idr_base_url, session, organism):

    """
    Return a list of screen ids in IDR
    for given case insensitive organism. (Uses the json api)
    """

    screenidList = []
    qs = {'base': idr_base_url, 'key': 'organism', 'value': organism}
    screens_projects_url = "{base}/mapr/api/{key}/?value={value}"
    url = screens_projects_url.format(**qs)
    for s in session.get(url).json()['screens']:
        screenidList.append(s['id'])

