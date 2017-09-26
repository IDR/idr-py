import pandas as pd
from attributes import get_phenotypes_for_genelist
from attributes import get_phenotypes_for_gene
from attributes import get_similar_genes
from attributes import get_organism_screenids
from connections import create_http_session, connection
from images import images_by_phenotype

from config import idr_base_url, organism


class TestAttributes():

    @classmethod
    def setup_class(cls):
        cls.session = create_http_session(idr_base_url)
        cls.conn = connection()

    def test_images_by_phenotype(self):

        images = images_by_phenotype(self.conn)
        assert (isinstance(images, list) is True)

    def test_get_organism_screenids(self):

        organisms = ['Homo sapiens',
                     'Saccharomyces cerevisiae',
                     'Schizosaccharomyces pombe',
                     'Drosophila melanogaster',
                     'Mus musculus',
                     'Arabidopsis thaliana']
        for idx, organism1 in enumerate(organisms):
            organism_screen_idlist = get_organism_screenids(idr_base_url,
                                                            self.session,
                                                            organism1)
            if idx < 4:
                assert (organism_screen_idlist != [])
            else:
                assert (organism_screen_idlist == [])

    def test_get_phenotypes_for_genelist(self):

        gene_list = ['CCS', 'SOD2', 'SOD3', 'SOD1']
        [query_genes_df,
         screen_to_phenotype_dict] = get_phenotypes_for_genelist(idr_base_url,
                                                                 self.session,
                                                                 gene_list,
                                                                 organism)

        assert isinstance(query_genes_df, pd.DataFrame)
        assert isinstance(screen_to_phenotype_dict, dict)
        assert not query_genes_df.empty
        print screen_to_phenotype_dict
        assert not bool(screen_to_phenotype_dict)

        [similar_genes,
         overlap_genes] = get_similar_genes(self.conn,
                                            gene_list,
                                            screen_to_phenotype_dict)

        assert isinstance(similar_genes, dict)
        assert isinstance(overlap_genes, dict)
        assert (similar_genes != [])
        assert (overlap_genes != [])

    def test_get_phenotypes_for_gene(self):

        gid = 'ARPC2'
        sid = 206
        uniquelist = get_phenotypes_for_gene(idr_base_url,
                                             self.session, gid)

        assert isinstance(uniquelist, pd.DataFrame)
        assert not uniquelist.empty
        uniquelist = get_phenotypes_for_gene(idr_base_url,
                                             self.session, gid, sid)

        assert isinstance(uniquelist, pd.DataFrame)
        assert not uniquelist.empty

    @classmethod
    def teardown_class(cls):
        cls.conn.close()
