import pandas as pd
from externalDBs import genes_of_interest_from_string
from externalDBs import network_of_interest
from externalDBs import get_entrezid
from externalDBs import get_ensembleid
from externalDBs import genes_of_interest_go
from externalDBs import ensembleid_to_genesymbol
from IPython.display import Image

from config import gene_symbol, taxonomy_id, endsemble_id


class Test_external_dbs():

    def test_genes_of_interest_from_string(self):
        intpartners = genes_of_interest_from_string(gene_symbol,
                                                    20,
                                                    taxonomy_id)
        assert isinstance(intpartners, pd.DataFrame)
        assert intpartners.empty is False

    def test_network_of_interest(self):
        int_image = network_of_interest(gene_symbol,
                                        20)
        assert isinstance(int_image, Image)

    def test_get_entrezid(self):
        entrezid = get_entrezid(gene_symbol)
        assert isinstance(entrezid, list)
        assert (entrezid is not None) is True
        # could do a proper assert for the returned id, but
        # given the regular updates in ids this assert
        # will break very often
        # so sticking to basic asserts

    def test_get_ensembleid(self):
        ensembleid = get_ensembleid(gene_symbol)
        assert isinstance(ensembleid, list)
        assert (ensembleid is not None) is True

    def test_genes_of_interest_go(self):
        go_gene_list = genes_of_interest_go('GO:0005885', taxonomy_id)
        assert isinstance(go_gene_list, list)
        assert (go_gene_list != []) is True

    def test_ensembleid_to_genesymbol(self):

        gene_symbol = ensembleid_to_genesymbol(endsemble_id)

        assert (isinstance(gene_symbol, str)
                or isinstance(gene_symbol, unicode)) is True
        assert (gene_symbol is not None) is True
