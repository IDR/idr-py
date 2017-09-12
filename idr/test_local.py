# from IPython.html import widgets
# from IPython.display import display

# from idr.connections import connection, create_http_session
# from idr.externalDBs import genes_of_interest_go
# from idr.widgets import textbox_widget
# from idr.widgets import select_organism_dropdown_widget

# go_gene_list = genes_of_interest_go(go_term.value, '9606')
# manual_list = ''
# manual_list = manual_gene_list.value.split(",")
# go_gene_list = list(set(go_gene_list + manual_list))
# print "Query list of genes:",go_gene_list

# organism = 'Homo Sapiens'
# idr_base_url = 'http://idr.openmicroscopy.org'
# session = create_http_session(idr_base_url)

# [query_genes_dataframe, screen_to_phenotype_dictionary] =
# get_phenotypes_for_genelist(idr_base_url, session, go_gene_list, organism)
# display(HTML(query_genes_dataframe.to_html( escape=False)))
