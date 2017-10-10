import pandas as pd
from idr import genes_of_interest_from_string
from idr import create_http_session, connection
from idr import get_phenotypes_for_genelist
from idr import get_similar_genes
from idr import plot_idr_attributes, plot_string_interactions

from config import go_gene_list, taxonomy_id, organism


class TestVisualizations():

    @classmethod
    def setup_class(cls):
        cls.session = create_http_session()
        cls.conn = connection()

    def test_plot_string_interactions(self):

        intpartners = genes_of_interest_from_string(go_gene_list,
                                                    20,
                                                    taxonomy_id)
        assert isinstance(intpartners, pd.DataFrame)
        assert not intpartners.empty

        df = plot_string_interactions(go_gene_list,
                                      go_gene_list,
                                      intpartners,
                                      False)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_plot_idr_attributes(self):

        [query_genes_df,
         screen_to_phenotype_dict] = get_phenotypes_for_genelist(self.session,
                                                                 go_gene_list,
                                                                 organism)
        query_genes_list = list(query_genes_df['Value'])
        [similar_genes,
         overlap_genes] = get_similar_genes(self.conn,
                                            query_genes_list,
                                            screen_to_phenotype_dict)

        [screenids_removed,
         phenotypes_removed,
         genes_of_interest] = plot_idr_attributes(similar_genes,
                                                  overlap_genes,
                                                  'int_test',
                                                  'Phenotypes',
                                                  0, 5,
                                                  False)

        assert isinstance(screenids_removed, list)
        assert isinstance(phenotypes_removed, list)
        assert isinstance(genes_of_interest, list)

        [screenids_removed,
         phenotypes_removed,
         genes_of_interest] = plot_idr_attributes(overlap_genes,
                                                  similar_genes,
                                                  'int_test',
                                                  'Screens',
                                                  0, 0,
                                                  False)

        assert isinstance(screenids_removed, list)
        assert isinstance(phenotypes_removed, list)
        assert isinstance(genes_of_interest, list)

    @classmethod
    def teardown_class(cls):
        cls.conn.close()
