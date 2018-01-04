"""
Helper functions for accessing the data from other databases from within
IPython notebooks.
"""
import requests
import pandas
from io import StringIO
from pandas import read_csv
import numpy as np
from IPython.display import Image


def genes_of_interest_from_string(gene_names,
                                  no_of_interacting_partners, taxonomyid):
    url = 'https://string-db.org/api/psi-mi-tab/interactionsList?identifiers='
    for g in gene_names:
        url = url + g + '%0d'
    url = (url + '&limit=' + str(no_of_interacting_partners) +
           '&network_flavor=evidence&species=' + taxonomyid)
    res = requests.get(url)
    df = read_csv(StringIO(res.text), sep='\t', header=None)
    c1 = df.loc[:, [2, 3, 14]]
    return c1


def network_of_interest(gene_names, no_of_interacting_partners):
    url = 'https://string-db.org/api/image/network?identifier='
    limit = str(no_of_interacting_partners) + '&network_flavor=evidence'
    for g in gene_names:
        url = url + g  # This doesn't look like it will work

    url = url + '&limit=' + limit
    return Image(url=url)


def get_entrezid(gene):
    """
    Use mygene.info api to convert gene_symbols to
    entrezgeneIds (gets ortholog ids as well)

    Note : This returns entrez ids for the gene in all organisms
    (Could consider taxonomy related entrez ids : if need be!)
    documentation for api:

    http://mygene.info/v3/api/#MyGene.info-gene-query-service-GET-Gene-query-service
    """
    entrezurl = "https://mygene.info/v3/query?q="
    entrezurl = entrezurl+gene

    res = requests.get(entrezurl)
    if not res.ok:
        return []

    results = pandas.read_json(StringIO(res.text))

    entrezid = []
    if results.empty:
        return entrezid

    for i in results.ix[:, 0]:
        key = i.keys()
        value = i.values()
        for cntr, k in enumerate(key):
            if k == 'entrezgene':
                entrezid.append(value[cntr])
                return entrezid


def get_ensembleid(gene):

    ensembleserver = "https://rest.ensembl.org/xrefs/symbol/homo_sapiens/"
    url = ensembleserver + gene + "?content-type=application/json"

    res = requests.get(url)
    results = pandas.read_json(StringIO(res.text))

    ensembleid = []
    if results.empty:
        return ensembleid

    for i in results.ix[:, 0]:
        ensembleid.append(i)
    return ensembleid


def genes_of_interest_go(go_term, taxonomy_id):

    url = ('https://www.ebi.ac.uk/QuickGO-Old/GAnnotation?tax=' +
           taxonomy_id +
           '&relType=IP&goid=%20' +
           go_term +
           '%20&format=tsv')
    res = requests.get(url)
    df = read_csv(StringIO(res.text), sep='\t', header=None)
    c1 = df.iloc[:, 3]
    genes = list(set(np.unique(c1.values.ravel())) - set(['Symbol', '-']))
    if genes == []:
        url = ('https://www.ebi.ac.uk/QuickGO-Old/GAnnotation?tax=' +
               taxonomy_id +
               '&goid=%20' +
               go_term +
               '%20&format=tsv')
        res = requests.get(url)
        df = read_csv(StringIO(res.text), sep='\t', header=None)
        c1 = df.ix[:, 3]
        genes = list(set(np.unique(c1.values.ravel())) - set(['Symbol', '-']))
    return genes


def ensembleid_to_genesymbol(ensembleid):

    ensembleserver = "https://rest.ensembl.org/xrefs/id/"
    url = (ensembleserver + ensembleid +
           "?content-type=application/json;external_db=WikiGene")
    res = requests.get(url)
    if not res.ok:
        return ensembleid
    if "error" in res.text:
        return ensembleid
    results = pandas.read_json(StringIO(res.text))
    if results.empty:
        return ensembleid
    symbol = results['display_id'][0]
    return symbol
