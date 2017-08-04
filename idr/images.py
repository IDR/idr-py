"""
Helper functions for accessing the IDR from within IPython notebooks.
"""
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
from attributes import annotation_ids_by_field


def images_by_phenotype(conn, phenotype="CMPO_0000077"):
    """
    Passes phenotype as the value argument to annotation_ids_by_field
    and loads Image objects which can be used for loading thumbnails, etc.
    """
    ann_ids = annotation_ids_by_field(conn, phenotype)
    return list(conn.getObjectsByAnnotations("Image", ann_ids))


def simple_colocalisation(image):
    """
    Perform a simple comparison of the red and green channels.

    Pearson coefficient described at
    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3074624/
    """
    p = image.getPrimaryPixels()

    # get 2D planes and reshape to 1D array
    r = p.getPlane(0, 0, 0)
    red = r.reshape(r.size)
    g = p.getPlane(0, 1, 0)
    green = g.reshape(g.size)

    # pearson colocalistion coefficient
    pearsonr(red, green)

    # scatter plot
    plt.scatter(red, green)
    plt.show()
