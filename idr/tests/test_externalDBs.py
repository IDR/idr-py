import pandas as pd
from idr import genes_of_interest_from_string
from idr import network_of_interest
from idr import get_entrezid
from idr import get_ensembleid
from idr import genes_of_interest_go
from idr import ensembleid_to_genesymbol
from IPython.display import Image

from config import gene_symbol, taxonomy_id, ensemble_id


class TestExternalDBs():

    def test_genes_of_interest_from_string(self):
        intpartners = genes_of_interest_from_string(gene_symbol,
                                                    20,
                                                    taxonomy_id)
        assert isinstance(intpartners, pd.DataFrame)
        assert not intpartners.empty

    def test_network_of_interest(self):
        int_image = network_of_interest(gene_symbol,
                                        20)
        assert isinstance(int_image, Image)

    def test_get_entrezid(self):
        entrezid = get_entrezid(gene_symbol)
        assert isinstance(entrezid, list)
        assert (entrezid is not None)
        # could do a proper assert for the returned id, but
        # given the regular updates in ids this assert
        # will break very often
        # so sticking to basic asserts

    def test_get_ensembleid(self):
        ensembleid = get_ensembleid(gene_symbol)
        assert isinstance(ensembleid, list)
        assert (ensembleid is not None)

    def test_genes_of_interest_go(self):
        go_gene_list = genes_of_interest_go('GO:0005885', taxonomy_id)
        assert isinstance(go_gene_list, list)
        assert (go_gene_list != [])

    def test_ensembleid_to_genesymbol(self):

        gene_symbol = ensembleid_to_genesymbol(ensemble_id)

        assert (isinstance(gene_symbol, str)
                or isinstance(gene_symbol, unicode))
        assert (gene_symbol is not None)
