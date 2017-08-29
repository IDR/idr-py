from collections import Counter
from collections import OrderedDict
from IPython import display
from IPython.display import clear_output
import matplotlib.pyplot as plt

def plot_idr_attributes(primary_dictionary, secondary_dictionary, Filter_by_category, Threshold_for_category, Threshold_for_plot):
    %matplotlib inline
    gene_counts = []  
    screenids_removed = []
    phenotypes_removed = []
    genes_of_interest = []
    for screenid in list(primary_dictionary.keys()):
        
        phenolist = []
        screens_list = []
        for phenoid in primary_dictionary[screenid].keys():
            phenolist = primary_dictionary[screenid][phenoid]
            phenolist1 = secondary_dictionary[screenid][phenoid]
            if Filter_by_category == 'Phenotypes':
                if len(phenolist1) < Threshold_for_category:
                    phenolist = []
                    phenotypes_removed.append(phenoid)
            screens_list = screens_list + phenolist
        
        if Filter_by_category == 'Screens':
            screens_list = list(set(screens_list)) 
        if len(screens_list) >= Threshold_for_category:
            gene_counts = gene_counts + screens_list
        else:
            screenids_removed.append(screenid)

    letter_counts = Counter(gene_counts)

    keystoremove = []
    for key, value in letter_counts.viewitems():
        if value < Threshold_for_plot:
            keystoremove.append(key)
            
    for keys in keystoremove:
        del letter_counts[keys]

    genes_of_interest = list(letter_counts.keys())
    df = pandas.DataFrame.from_dict(OrderedDict(letter_counts.most_common()), orient='index')
    if df.empty:
        print('DataFrame is empty, please reduce thresholds!')
    else:
        ax = df.plot(kind='bar',figsize=(30, 15), fontsize=18)
        ax.set_title(plot_title, fontsize=18)
        ax.set_xlabel("Genes", fontsize=18)
        ax.set_ylabel("Number of Unique" + Filter_by_category + "in IDR", fontsize=18)
        plt.show()
        return screenids_removed, phenotypes_removed, genes_of_interest


def plot_string_interactions(primary_list, secondary_list,total_interactions_dataframe, plot_title):
    
    intdict = OrderedDict()
    for gene in secondary_list:
        c2 = (total_interactions_dataframe.loc[total_interactions_dataframe[2] == gene])
        c3 = (total_interactions_dataframe.loc[total_interactions_dataframe[3] == gene])

        totlist = set(list(c2[3]) + list(c3[2]))
        intwithsublist = len(totlist.intersection(primary_list))
        if (intwithsublist)>0:
            intdict[gene] = [intwithsublist]
    df = pandas.DataFrame.from_dict(intdict, orient='index')
    df.columns = [plot_title]
    df = df.sort_values(by=[plot_title], ascending=[False])
    ax = df.plot(kind='bar', figsize=(30, 15), fontsize=18)
    ax.set_title("String Interactions of similar genes with " + plot_title + "(minimum one interaction atleast with query set)", fontsize=18)
    ax.set_xlabel("Gene Symbols", fontsize=18)
    ax.set_ylabel("Number Of interactions in String Database", fontsize=18)
    ax.legend()
    plt.show()