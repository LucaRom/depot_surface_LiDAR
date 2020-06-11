# 1- Créer le cadre avec la référence
# 2- Différence cadre - zone de dépots
# 3- Histogramme zonal couche de dépôts
# 4- Histogramme zonal zone ext
# 5- Extraction des colonnes dans les histogrammes
# 6- Représentation graphique

import rasterstats
from osgeo import gdal
import os
from ech_pixel import creation_cadre
from pretraitements import clip_raster_to_polygon

root_dir = os.path.abspath(os.path.dirname(__file__))
path_depot = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\inputs\depots\31H02NE\zones_depots_glaciolacustres_31H02NE.shp'
pred_31H02NE =r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\outputs\pixel\prediction_31H02NE.tif'
pred_31H02SE = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\outputs\pixel\prediction_31H02SE.tif'
pred_31H02SO = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\outputs\pixel\prediction_31H02SO.tif'
path_mnt = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\inputs\MNT\resample'

pred_31H02SO_32D01 = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\outputs\pixel\prediction_31H02SO_32D01.tif'
pred_32D02SE_31H02 = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\outputs\pixel\prediction_32D02SE_31H02.tif'
pred_32D02SE_32D01 = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\outputs\pixel\prediction_32D02SE_32D01.tif'


def clip_final(feuillet, mod, output):
    '''
    :param feuillet: No. feuillet avec un buffer à clipper (str)
    :param reference: Chemin raster de référence pour les dimensions du clip (str)
    :param output: Chemin du fichier de sortie (str)
    :return: Clip du feuillet en entrée clippé à la largeur du feuillet original (.tif)
    '''
    # Chemin du fichier de calssification dans le répertoire racine
    path_feuillet = os.path.join(root_dir, 'outputs/pixel/prediction_{}_{}_epsg.tif'.format(feuillet, mod))

    # Chemin du fichier de référence pour clip dans le répertoire racine
    path_ref = os.path.join(root_dir, 'inputs/MNT/resample/MNT_{}_resample.tif'.format(feuillet))

    # Création du cadre pour le clip
    cadre, epsg, nodata = creation_cadre(path_ref)

    # Clip
    clip_raster_to_polygon(path_feuillet, cadre, epsg, nodata, output)
    return cadre



def creation_raster (inputArray,inputMet, drv, output):
    '''
    :param inputArray: Array à transformer en Raster (np.array)
    :param inputMet: Chemin du Raster de référence pour les dimensions et le CRS (str)
    :return: Raster géoréférencé de l'array en entrée. La sauvegarde est effectuée en mémoire (gdal.dataset)
    '''
    # je déclare tous les drivers
    gdal.AllRegister()
    # le driver que je veux utiliser
    driver = gdal.GetDriverByName(drv)

    # taille de mon image (ce sera la taille de la matrice)
    rows, cols = inputArray.shape

    # je déclare mon image
    image = driver.Create(output, cols, rows, 1, gdal.GDT_Float64)

    # J'extrais les paramètres d'une métriques pour le positionnement du fichier sortant
    data = gdal.Open(inputMet, gdal.GA_ReadOnly)
    geoTransform = data.GetGeoTransform()
    proj = data.GetProjection()
    nodata = data.GetRasterBand(1).GetNoDataValue()
    data = None # On vide la mémoire

    # j'écris la matrice dans la bande 1 du fichier sortant
    image.GetRasterBand(1).WriteArray(inputArray, 0, 0)

    # On donne les paramètres de la métrique au fichier sortant
    image.GetRasterBand(1).SetNoDataValue(nodata)
    image.SetProjection(proj)
    image.SetGeoTransform(geoTransform)
    image.FlushCache()

    # si on veut une image en mémoire, on retourne le dataset et la projection, sinon on vide la mémoire
    if drv == 'MEM':
        return image, proj
    else:
        image = None



#liste_pred = [pred_31H02NE, pred_31H02SE, pred_31H02SO]
liste_pred = [pred_31H02SO_32D01, pred_32D02SE_31H02, pred_32D02SE_32D01]
for pred in liste_pred:
    feuillet = os.path.basename(pred).split('_')[1]
    mod = os.path.basename(pred).split('_')[2][:-4]
    data = gdal.Open(pred)
    nd = data.GetRasterBand(1).GetNoDataValue()
    data_array = data.GetRasterBand(1).ReadAsArray()
    output_epsg = os.path.join(os.path.dirname(pred), 'prediction_{}_{}_epsg.tif'.format(feuillet, mod))

    mnt_resample = os.path.join(path_mnt, 'MNT_{}_resample.tif'.format(feuillet))
    print(mnt_resample)
    creation_raster(data_array, mnt_resample, 'GTiff', output_epsg)

    output_clip = os.path.join(os.path.dirname(pred), 'prediction_{}_{}_epsg_clip.tif'.format(feuillet, mod))
    clip_final(feuillet, mod, output_clip)






# import rasterio
#
# path_mnt1 = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\inputs\MNT\originaux\31H02\MNT_31H02NE.tif'
# pred_31H02NE_epsg =r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\outputs\pixel\prediction_31H02NE_epsg.tif'
#
# # with rasterio.open(pred_31H02NE_epsg) as raster:
# #     nodata = raster.nodatavals
# #     print(nodata)
# #
# # d = gdal.Open(pred_31H02NE_epsg)
# # nodata = d.GetRasterBand(1).GetNoDataValue()
# # print(nodata)