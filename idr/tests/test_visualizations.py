from externalDBs import genes_of_interest_from_string
from connections import create_http_session, connection
from attributes import get_phenotypes_for_genelist
from attributes import get_similar_genes
from visualizations import plot_idr_attributes, plot_string_interactions
import pandas as pd
from config import idr_base_url, go_gene_list, taxonomy_id, organism

import matplotlib.pyplot as plt


class Test_visualizations():

    import matplotlib.pyplot as plt
    session = create_http_session(idr_base_url)
    conn = connection()

    def test_plot_string_interactions(self):

        intpartners = genes_of_interest_from_string(go_gene_list,
                                                    20,
                                                    taxonomy_id)
        assert isinstance(intpartners, pd.DataFrame)
        assert intpartners.empty is False

        df = plot_string_interactions(go_gene_list,
                                      go_gene_list,
                                      intpartners)

        assert isinstance(df, pd.DataFrame) is True
        assert df.empty is False
        plt.close('all')

    def test_plot_idr_attributes(self):

        import matplotlib.pyplot as plt
        [query_genes_df,
         screen_to_phenotype_dict] = get_phenotypes_for_genelist(idr_base_url,
                                                                 self.session,
                                                                 go_gene_list,
                                                                 organism)
        query_genes_list = list(query_genes_df['Value'])
        [similar_genes,
         overlap_genes] = get_similar_genes(self.conn,
                                            query_genes_list,
                                            screen_to_phenotype_dict)

        [screenids_removed,
         phenotypes_removed,
         genes_of_interest] = plot_idr_attributes(overlap_genes,
                                                  similar_genes,
                                                  'int_test',
                                                  'Phenotypes',
                                                  0, 0)

        assert isinstance(screenids_removed, list) is True
        assert isinstance(phenotypes_removed, list) is True
        assert isinstance(genes_of_interest, list) is True

        [screenids_removed,
         phenotypes_removed,
         genes_of_interest] = plot_idr_attributes(overlap_genes,
                                                  similar_genes,
                                                  'int_test',
                                                  'Screens',
                                                  0, 0)

        assert isinstance(screenids_removed, list) is True
        assert isinstance(phenotypes_removed, list) is True
        assert isinstance(genes_of_interest, list) is True
        plt.close('all')
    conn.close()
