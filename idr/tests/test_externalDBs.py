from externalDBs import genes_of_interest_from_string, network_of_interest, get_entrezid, get_ensembleid, genes_of_interest_go, ensembleid_to_genesymbol
from connections import create_http_session, connection
from config import *
import pandas as pd
from IPython.display import Image

import pytest


class Test_external_dbs():

    def test_genes_of_interest_from_string(self):
        intpartners = genes_of_interest_from_string(gene_symbol,
                                                 20,
                                                 taxonomy_id)
        assert isinstance(intpartners, pd.DataFrame)
        assert intpartners.empty == False


    def test_network_of_interest(self):
        int_image = network_of_interest(gene_symbol,
                                        20)
        assert isinstance(int_image, Image)


    def test_get_entrezid(self):
        entrezid = get_entrezid(gene_symbol)
        assert isinstance(entrezid, list)
        assert (entrezid != None) == True
        # could do a proper assert for the returned id, but 
        # given the regular updates in ids this assert 
        # will break very often
        # so sticking to basic asserts


    def test_get_ensembleid(self):
        ensembleid = get_ensembleid(gene_symbol)
        assert isinstance(ensembleid, list)
        assert (ensembleid != None) == True


    def test_genes_of_interest_go(self):
        go_gene_list = genes_of_interest_go('GO:0005885', taxonomy_id)
        assert isinstance(go_gene_list, list)
        assert (go_gene_list != []) == True


    def test_ensembleid_to_genesymbol(self):

        gene_symbol = get_ensembleid(endsemble_id)
        assert isinstance(gene_symbol, list)
        assert (gene_symbol != None) == True

