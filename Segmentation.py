# -*- coding: utf-8 -*-

"""
Created on Wed Jan 2020
@authors: David Ethier  david.ethier2@usherbrooke.ca
          Luca Romanini luca.romanini@usherbrooke.ca

"""

from ech_pixel import creation_cadre, creation_raster, conversion_polygone, creation_buffer
#import osr
#import numpy as np
from skimage.color import rgb2gray
from skimage.filters import sobel
from skimage.segmentation import watershed
from skimage.util import img_as_float64
from skimage import io
#from osgeo import osr
from osgeo.gdalnumeric import *
import geopandas as gpd


def segmentation(input_met, markers, compactness):
    '''
    :param input_met: Raster 1 bande sur laquelle on veut faire la segmentation (.tif)
    :param markers: Nombre de polygone voulu dans la segmentation (int)
    :param compactness: Influence la forme des polygones, ex: 0.02 (float)
    :return: Numpy array de la segmentation

    *** EDIT: Seul la segmentation watershed est implémentée***
    '''

    # Empilage de 3x l'image à segmenter pour simuler une image RGB
    img1 = img_as_float64(io.imread(input_met))
    img2 = img_as_float64(io.imread(input_met))
    img3 = img_as_float64(io.imread(input_met))
    img = np.dstack([img1, img2, img3])

    # Segmentation
    gradient = sobel(rgb2gray(img))
    segments = watershed(gradient, markers=markers, connectivity=True, mask=None, compactness=compactness, watershed_line=False) #selon la surface du feuillet, "markers" peut varier de 7000 à 8000
    return segments


def segmentation_main(input_met, markers, compactness, output):
    '''
    :param input_met: Raster 1 bande sur laquelle on veut faire la segmentation (.tif)
    :param markers: Nombre de polygone voulu dans la segmentation (int)
    :param compactness: Influence la forme des polygones, ex: 0.02 (float)
    :param output: Chemin du fichier de sortie (str)
    :return: Une couche polygonale de la segmentation sans les polygones à l'extérieur du cadre de l'image (.shp)
    '''

    # Segmentation
    print('Segmentation...')
    seg = segmentation(input_met, markers, compactness)

    # Conversion du Numpy array en raster
    print('Création du raster...')
    ras, proj = creation_raster(inputMet=input_met, inputArray=seg)

    # Conversion du raster en polygones
    print('Création de la couche polygonale...')
    path_seg_poly = "/vsimem/seg.shp"
    conversion_polygone(dataset=ras, output=path_seg_poly)

    # Création du cadre du raster input
    print('Création du cadre...')
    cadre, epsg, nodata = creation_cadre(input_met)


    # Suppression des géométries invalides
    print('Suppression géométries invalides...')
    seg_poly = gpd.read_file(path_seg_poly)
    seg_poly_rep = creation_buffer(seg_poly, 0, epsg, 1, 1)
    # Suppresion d'une colonne inutile
    for col in seg_poly_rep.columns:
        if col == 'FID':
            del seg_poly_rep[col]

    # On sélectionne seulement les polygones à l'intérieur du cadre
    print('Suppression des polygones en dehors du cadre...')
    geom_cadre = cadre.loc[0, 'geometry']
    seg_clip = gpd.GeoDataFrame(columns=['geometry'])
    seg_clip.crs = epsg
    index = 0
    for ind, row in seg_poly_rep.iterrows():
        geom = row['geometry']
        if geom.within(geom_cadre):
            seg_clip.loc[index, 'geometry'] = geom
            index += 1

    # Sauvegarde
    print('Sauvegarde...')
    seg_clip.to_file(output)

    print('Terminé')


if __name__ == "__main__":

    input_met = r"C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\inputs\tiffs\31H02SO\Pen_WB_31H02SO.tif"
    input_tif_cadre = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\inputs\MNT\resample\MNT_31H02SO_resample.tif'
    output = r"C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\inputs\segmentations\segmentation_31H02SO.shp"
    type_seg = 'watershed'

    segmentation_main(input_met=input_met, markers=5000, compactness=0.02,  output=output)
