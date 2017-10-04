from collections import Counter
from collections import OrderedDict
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from externalDBs import ensembleid_to_genesymbol


def plot_idr_attributes(primary_dictionary,
                        secondary_dictionary,
                        plot_title,
                        filter_by_category,
                        threshold_for_category,
                        threshold_for_plot,
                        plot_condition=True):
    gene_counts = []
    screenids_removed = []
    phenotypes_removed = []
    genes_of_interest = []
    query_list = []
    for screenid in list(primary_dictionary.keys()):
        phenolist = []
        screens_list = []
        query_list = []
        for phenoid in primary_dictionary[screenid].keys():
            phenolist = primary_dictionary[screenid][phenoid]
            phenolist1 = secondary_dictionary[screenid][phenoid]
            if filter_by_category == 'Phenotypes':
                if len(phenolist1) < threshold_for_category:
                    phenolist = []
                    phenotypes_removed.append(phenoid)
            screens_list = screens_list + phenolist
            query_list = query_list + phenolist1

        if filter_by_category == 'Screens':
            screens_list = list(set(screens_list))
        if len(screens_list) >= threshold_for_category:
            gene_counts = gene_counts + screens_list
        else:
            screenids_removed.append(screenid)
    letter_counts = Counter(gene_counts)
    keystoremove = []
    for key, value in letter_counts.viewitems():
        if value < threshold_for_plot:
            keystoremove.append(key)
    for keys in keystoremove:
        del letter_counts[keys]
    query_list = list(set(query_list))
    letter_counts = OrderedDict(letter_counts.most_common())

    if primary_dictionary != secondary_dictionary:
        dict1 = OrderedDict()
        for k, v in letter_counts.iteritems():
            key = k
            if k.startswith('ENSG'):
                key = ensembleid_to_genesymbol(k)
                if key in dict1:
                    value1 = dict1[key]
                    if value1 > v:
                        v = value1
            if key in list(query_list):
                print ('in query list')
                continue
            dict1[key] = v
        letter_counts = dict1

    if '' in letter_counts:
        del letter_counts['']

    genes_of_interest = list(letter_counts.keys())

    df = pandas.DataFrame.from_dict(letter_counts, orient='index')

    if plot_condition is True:
        if df.empty:
            print('DataFrame is empty, please reduce thresholds!')
            hf, ha = plt.subplots(1, 1)
        else:
            ax = df.plot(kind='bar', figsize=(30, 15), fontsize=18)
            ax.set_title(plot_title, fontsize=18)
            ax.set_xlabel("Genes", fontsize=18)
            ax.set_ylabel("Number of Unique"
                          + filter_by_category + "in IDR", fontsize=18)
        plt.show()
    else:
        print("Plots are currently" +
              "shown in the notebooks alone"
              " and not from the terminal")

    return screenids_removed, phenotypes_removed, genes_of_interest


def plot_string_interactions(primary_list,
                             secondary_list,
                             total_interactions_dataframe,
                             plot_condition=True):
    dict1 = {}
    for gene in primary_list:
        c2 = total_interactions_dataframe.loc[total_interactions_dataframe[2]
                                              == gene]
        c3 = total_interactions_dataframe.loc[total_interactions_dataframe[3]
                                              == gene]
        c4 = pandas.concat([c2, c3])

        dict1[str(gene)] = {}
        totlist = set(list(c2[3]) + list(c3[2]))
        intwithsublist = totlist.intersection(secondary_list)
        if len(intwithsublist) > 0:
            for gene1 in intwithsublist:
                c5 = c4.loc[c4[2] == gene1]
                if c5.empty:
                    c5 = c4.loc[c4[3] == gene1]
                score = str(c5[14])
                stid = score.index('score:')
                endid = score.index('|')
                dict1[str(gene)][gene1] = float(score[stid+6:endid])

    df = pandas.DataFrame.from_dict(dict1, orient='index')
    df = df.fillna(value=int(0))
    df['ColTotal'] = df.sum(axis=1)
    df.loc['RowTotal'] = df.sum()
    df = df.sort_values(by='RowTotal', ascending=False, axis=1)
    df = df.sort_values(by='ColTotal', ascending=False)
    df = df.drop(['RowTotal'])
    df = df.drop(['ColTotal'], axis=1)

    if plot_condition is True:
        if len(df.columns) == 1 or len(df.index) == 1:
            sns.heatmap(df)
            plt.show()
        elif df.empty:
            print('No primary interactors found')
        else:
            g = sns.clustermap(df)
            plt.setp(g.ax_heatmap.yaxis.get_majorticklabels(), rotation=0)
            plt.show()
    else:
        print("Plots are currently" +
              "shown in the notebooks alone"
              " and not from the terminal")
    return df
