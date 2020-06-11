# 1- Créer le cadre avec la référence
# 2- Différence cadre - zone de dépots
# 3- Histogramme zonal couche de dépôts
# 4- Histogramme zonal zone ext
# 5- Extraction des colonnes dans les histogrammes
# 6- Représentation graphique

import rasterstats
import glob
from osgeo import gdal
import os
from ech_pixel import creation_cadre, dissolve
from pretraitements import clip_raster_to_polygon
from ech_pixel import difference
import geopandas as gpd
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt

root_dir = os.path.abspath(os.path.dirname(__file__))

def clip_final(path_feuillet, output):
    '''
    :param feuillet: No. feuillet avec un buffer à clipper (str)
    :param reference: Chemin raster de référence pour les dimensions du clip (str)
    :param output: Chemin du fichier de sortie (str)
    :return: Clip du feuillet en entrée clippé à la largeur du feuillet original (.tif)
    '''
    # Chemin du fichier de calssification dans le répertoire racine
    feuillet = os.path.basename(path_feuillet).split('_')[1]
   # path_feuillet = os.path.join(root_dir, 'outputs/pixel/prediction_{}_{}_epsg.tif'.format(feuillet, mod))


    # Chemin du fichier de référence pour clip dans le répertoire racine
    path_ref = os.path.join(root_dir, 'Backup/MNT_{}_resample.tif'.format(feuillet))

    # Création du cadre pour le clip
    cadre, epsg, nodata = creation_cadre(path_ref)

    # Clip
    clip_raster_to_polygon(path_feuillet, cadre, epsg, 255, output)
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
    image = driver.Create(output, cols, rows, 1, gdal.GDT_Byte)

    # J'extrais les paramètres d'une métriques pour le positionnement du fichier sortant
    data = gdal.Open(inputMet, gdal.GA_ReadOnly)
    geoTransform = data.GetGeoTransform()
    proj = data.GetProjection()
    #nodata = data.GetRasterBand(1).GetNoDataValue()
    data = None # On vide la mémoire

    # j'écris la matrice dans la bande 1 du fichier sortant
    image.GetRasterBand(1).WriteArray(inputArray, 0, 0)

    # On donne les paramètres de la métrique au fichier sortant
    image.GetRasterBand(1).SetNoDataValue(255)
    image.SetProjection(proj)
    image.SetGeoTransform(geoTransform)
    image.FlushCache()

    # si on veut une image en mémoire, on retourne le dataset et la projection, sinon on vide la mémoire
    if drv == 'MEM':
        return image, proj
    else:
        image = None

# #liste_pred = [pred_31H02NE, pred_31H02SE, pred_31H02SO]
# # liste_pred = [pred_31H02SO_32D01, pred_32D02SE_31H02, pred_32D02SE_32D01]
# path_data = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\fichiers_outputs\pixel'
# path_output = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\fichiers_outputs\pred_pixel'
# liste_pred = glob.glob(os.path.join(path_data, '*.tif'))
# for pred in liste_pred:
#     feuillet = os.path.basename(pred).split('_')[1]
#     name = os.path.basename(pred)
#     mod = os.path.basename(pred).split('_')[2][:-4]
#     data = gdal.Open(pred)
#     nd = data.GetRasterBand(1).GetNoDataValue()
#     data_array = data.GetRasterBand(1).ReadAsArray()
#     output_epsg = os.path.join(path_output, name)
#
#     mnt_resample = os.path.join(root_dir, 'Backup/MNT_{}_resample.tif'.format(feuillet))
#     print(mnt_resample)
#     creation_raster(data_array, mnt_resample, 'GTiff', output_epsg)
#
#     output_clip = os.path.join(path_output, '{}_clip.tif'.format(name[:-4]))
#     clip_final(output_epsg, output_clip)


#path_data = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\fichiers_outputs\pred_pixel'
#path_depot = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\inputs\depots'
#liste_clip = glob.glob(os.path.join(path_data, '*clip.tif'))

#for clip in liste_clip:

def creation_matrice_confusion(path_raster, path_depot):

    name = os.path.basename(path_raster)
    feuillet = name.split('_')[1]
    path_depot_feuillet = os.path.join(path_depot, feuillet,  'zones_depots_glaciolacustres_{}.shp'.format(feuillet))

    # création du cadre
    cadre, epsg, nodata = creation_cadre(path_raster)

    # Copie depots
    depot = gpd.read_file(path_depot_feuillet)
    depot_dissolve = dissolve(depot, epsg)

    # difference cadre - depots
    zone_ext = difference(cadre, depot, epsg)

    # Extraction stats zonales zone ext
    zone_ext_stats = rasterstats.zonal_stats(zone_ext, path_raster, stats=['sum','count'])[0]
    no_1_pred_ext = int(zone_ext_stats['sum'])
    no_0_pred_ext = int(zone_ext_stats['count']) - no_1_pred_ext

    # Extraction stats  zonales zone int
    zone_int_stats = rasterstats.zonal_stats(depot_dissolve, path_raster, stats=['sum', 'count'])[0]
    no_1_pred_int = int(zone_int_stats['sum'])
    no_0_pred_int = int(zone_int_stats['count']) - no_1_pred_int

    # Calcul exactitude globale
    no_pix_total = int(zone_ext_stats['count']) + int(zone_int_stats['count'])
    exact_glob = 'Exactitude globale {:.2f} %'.format(((no_0_pred_ext + no_1_pred_int)/no_pix_total) * 100)
    print(exact_glob)

    # Création de la matrice de confusion
    arr = [[no_0_pred_ext, no_1_pred_ext],
           [no_0_pred_int, no_1_pred_int]]
    matrice_data = pd.DataFrame(arr, index=['0', '1'], columns=['0', '1'])

    sn.set(font_scale=1.2)  # for label size
    sn.heatmap(matrice_data,
               annot=True,
               annot_kws={"size": 14}, # font size
               cmap=plt.cm.Blues,
               fmt = 'd'
               )
    plt.title('{} - {}'.format(feuillet, exact_glob))
    plt.xlabel('Prédit')
    plt.ylabel('Réel')
    plt.show()


path_data = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\fichiers_outputs\pred_pixel'
path_depot = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\inputs\depots'
liste_clip = glob.glob(os.path.join(path_data, '*clip.tif'))

for clip in liste_clip:
    creation_matrice_confusion(clip, path_depot)


