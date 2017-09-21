from attributes import get_phenotypes_for_genelist
from attributes import get_phenotypes_for_gene 
from attributes import get_similar_genes
from attributes import get_organism_screenids
from connections import create_http_session, connection
import pandas as pd

from config import *

import pytest

class Test_attributes():

    session = create_http_session(idr_base_url)
    conn = connection(hostname, username, password, 4064)


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
            if idx<4:
                assert (organism_screen_idlist == []) == False
            else:
                assert (organism_screen_idlist == []) == True


    def test_get_phenotypes_for_geneList(self):

        gene_list = ['CCS', 'SOD2', 'SOD3', 'SOD1']
        [query_genes_dataframe, screen_to_phenotype_dictionary] = get_phenotypes_for_genelist(idr_base_url,
                                                                                              self.session,
                                                                                              gene_list,
                                                                                              organism)
            

        assert isinstance(query_genes_dataframe, pd.DataFrame) == True
        assert isinstance(screen_to_phenotype_dictionary, dict) == True
        assert query_genes_dataframe.empty == False
        print screen_to_phenotype_dictionary
        assert bool(screen_to_phenotype_dictionary) == False

        [similar_genes, overlap_genes] = get_similar_genes(self.conn, 
                                                           gene_list,
                                                           screen_to_phenotype_dictionary)

        assert isinstance(similar_genes, dict) == True
        assert isinstance(overlap_genes, dict) == True
        assert (similar_genes == []) == False
        assert (overlap_genes == []) == False


    def test_get_phenotypes_for_gene(self):

        gid = 'ARPC2'
        sid = 206
        uniquelist = get_phenotypes_for_gene(idr_base_url,
                                             self.session, gid)

        assert isinstance(uniquelist, pd.DataFrame) == True
        assert uniquelist.empty == False
        uniquelist = get_phenotypes_for_gene(idr_base_url,
                                             self.session, gid, sid)

        assert isinstance(uniquelist, pd.DataFrame) == True
        assert uniquelist.empty == False


    def test_images_by_phenotype(self):

        images = images_by_phenotype(conn)
        assert (isinstance(images, list) == True)

    conn.close()
    
