from ech_pixel import creation_cadre, creation_raster, conversion_polygone, creation_buffer
import osr
import numpy as np
from skimage.color import rgb2gray
from skimage.filters import sobel
from skimage.segmentation import watershed
from skimage.util import img_as_float64
from skimage import io
from osgeo import osr
from osgeo.gdalnumeric import *
import geopandas as gpd


def segmentation(input_met, type_seg):
    '''
    :param input_met: Raster 1 bande sur laquelle on veut faire la segmentation (.tif)
    :param type_seg: Type de segmentation désirée (watershed, slic, quickshift, felzenszwalb)
    :return: Numpy array de la segmentation

    *** EDIT: Seul la segmentation watershed est implémentée***
    '''

    # Empilage de 3x l'image à segmenter pour simuler une image RGB
    img1 = img_as_float64(io.imread(input_met))
    img2 = img_as_float64(io.imread(input_met))
    img3 = img_as_float64(io.imread(input_met))
    img = np.dstack([img1, img2, img3])

    # Méthode de la conversion en double
    # pil_im = Image.open(input_met, 'r')
    # img = np.asarray(pil_im, dtype=np.double)

    # Segmentation
    segments = None
    if type_seg.lower() in ['watershed', 'ws']:
        gradient = sobel(rgb2gray(img))
        segments = watershed(gradient, markers=8000, connectivity=True, mask=None, compactness=0.0025, watershed_line=False) #selon la surface du feuillet, "markers" peut varier de 7000 à 8000
    return segments


def segmentation_main(input_met, type_seg, output):
    '''
    :param input_met: Raster 1 bande sur laquelle on veut faire la segmentation (.tif)
    :param type_seg: Type de segmentation désirée (watershed, slic, quickshift, felzenszwalb)
    :param output: Chemin du fichier de sortie (str)
    :return: Une couche polygonale de la segmentation sans les polygones à l'extérieur du cadre de l'image (.shp)
    '''

    # Segmentation
    print('Segmentation...')
    seg = segmentation(input_met, type_seg)

    # Conversion du Numpy array en raster
    print('Création du raster...')
    ras, proj = creation_raster(inputMet=input_met, inputArray=seg)

    # Conversion du raster en polygones
    print('Création de la couche polygonale...')
    path_seg_poly = "/vsimem/seg.shp"
    conversion_polygone(dataset=ras, output=path_seg_poly)

    # Création du cadre du raster input
    print('Création du cadre...')
    cadre, epsg = creation_cadre(input_met)


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

    segmentation_main(input_met=input_met, type_seg=type_seg,  output=output)
