
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
from matplotlib.ticker import FuncFormatter

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
# #
# #     output_clip = os.path.join(path_output, '{}_clip.tif'.format(name[:-4]))
# #     clip_final(output_epsg, output_clip)


#path_data = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\fichiers_outputs\pred_pixel'
#path_depot = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\inputs\depots'
#liste_clip = glob.glob(os.path.join(path_data, '*clip.tif'))

#for clip in liste_clip:

def matrice_confusion_pixel(path_raster, path_depot):

    name = os.path.basename(path_raster)
    name_split = name.split('_')
    feuillet = name_split[1]
    modele = name_split[2]
    path_depot_feuillet = path_depot #os.path.join(path_depot, feuillet,  'zones_depots_glaciolacustres_{}.shp'.format(feuillet))

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

    # Création du array pour la matrice
    array_matrice = [[no_0_pred_ext, no_1_pred_ext],
                    [no_0_pred_int, no_1_pred_int]]

    return array_matrice


def matrice_confusion_objet(input_pred, path_depot, path_raster_cadre):
    shp = gpd.read_file(input_pred)
    aire_totale = sum(shp.area.values)

    # Zone dépot reelle
    depot_multi = gpd.read_file(path_depot)
    depot = dissolve(depot_multi, depot_multi.crs)

    # Création de la zone externe réelle
    print('Création de la zone externe réelle')
    cadre, epsg, nodata = creation_cadre(path_raster_cadre)
    zone_ext = difference(cadre, depot, epsg)
    #zone_ext.to_file(os.path.join(path_out, 'zone_ext.shp'))

    # Multipolygon des polygon prédits comme 1
    print('Multipolygon des polygon prédits comme 1')
    pred1 = shp[shp['prediction'] == 1]
    pred1 = dissolve(pred1, epsg)
    #pred1.to_file(os.path.join(path_out, 'pred1_dissolve.shp'))
    aire_totale_classe_1 = sum(pred1.area.values)

    # Multipolygon des polygones prédits comme 0
    print('Multipolygon des polygones prédits comme 0')
    pred0 = shp[shp['prediction'] == 0]
    pred0 = dissolve(pred0, epsg)
    #pred0.to_file(os.path.join(path_out, 'pred0_dissolve.shp'))
    aire_totale_classe_0 = sum(pred0.area.values)

    # Aire totale bien classé pour 0
    print('Aire totale bien classé pour 0')
    diff0 = difference(pred0, depot, epsg)
    #diff0.to_file(os.path.join(path_out, 'diff0.shp'))
    aire_bien_classe_0 = sum(diff0.area.values)
    print(aire_bien_classe_0)

    # Aire totale bien classée pour 1
    print('Aire totale bien classée pour 1')
    diff1 = difference(pred1, zone_ext, epsg)
    #diff1.to_file(os.path.join(path_out, 'diff1.shp'))
    aire_bien_classe_1 = sum(diff1.area.values)
    print(aire_bien_classe_1)

    # Aire totale mal classée pour 0 (commission 0)
    print('Aire totale mal classée pour 0 (commission 0)')
    aire_mal_classe_0 = aire_totale_classe_0 - aire_bien_classe_0
    print(aire_mal_classe_0)

    # Aire totale mal classée pour 1 (commission 1)
    print('Aire totale mal classée pour 1 (commission 1)')
    aire_mal_classe_1 = aire_totale_classe_1 - aire_bien_classe_1
    print(aire_mal_classe_1)

    print('Aire totale')
    print(aire_totale)
    print('somme des aires')
    print(aire_bien_classe_1 + aire_bien_classe_0 + aire_mal_classe_1 + aire_mal_classe_0)

    array_matrice = [[aire_bien_classe_0, aire_mal_classe_1],
                     [aire_mal_classe_0, aire_bien_classe_1]]

    return array_matrice


def plot_matrice(array_matrice, feuillet, modele, approche):

    # Calcul exactitude globale
    exact_glob = ((array_matrice[0][0] + array_matrice[1][1])/(array_matrice[0][0] + array_matrice[0][1] +
                                                              array_matrice[1][0] + array_matrice[1][1])) * 100

    # Formattage de la matrice selon l'approche choisi
    array_format = None
    fmt_annot = None
    cbar_kws = None

    # Approche par objet, on va afficher en km2 avec une précision au mètre
    if 'objet' in approche.lower():
        array_format = [[float(i/1000000) for i in array_matrice[0]],
                        [float(j/1000000) for j in array_matrice[1]]]
        fmt = '.3f'
    else:
    # Approche par pixel, on affiche en nombre de pixels
        array_format = array_matrice

        # Format des chiffres dans les cases pour que ce soit en notation normale
        comma_fmt = FuncFormatter(lambda x, p: format(int(x), ','))
        cbar_kws = {'format': comma_fmt}
        fmt = 'd'

    # Création de l'affichage
    matrice_data = pd.DataFrame(array_format, index=['0', '1'], columns=['0', '1'])
    sn.set(font_scale=1.2)  # for label size
    matrice = sn.heatmap(matrice_data,
               annot=True,
               annot_kws={"size": 14}, # font size
               cmap=plt.cm.Blues,
               fmt = fmt,
               cbar_kws=cbar_kws
               )
    if 'pixel' in approche.lower():
        for t in matrice.texts:
            t.set_text('{:,d}'.format(int(t.get_text())))
    plt.title('{} - Modèle {}\nApproche par {} - Exactitude globale: {:.2f} %'.format(feuillet, modele, approche, exact_glob))
    plt.xlabel('Prédit')
    plt.ylabel('Réel')
    plt.show()


# rep_pred = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\fichiers_outputs\objet'
# rep_depot = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\inputs\depots'
# rep_raster_cadre = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\Backup'
# #path_out = r'C:\Users\home\Documents\Documents\APP3\test_matrice'


# liste_shp = glob.glob(os.path.join(rep_pred, '*.shp'))
# for i in liste_shp:
#     name = os.path.basename(i)[:-4]
#     print(name)
#     name_split = name.split('_')
#     feuillet = name_split[3]
#     modele = name_split[5]
#     path_depot = os.path.join(rep_depot, feuillet, 'zones_depots_glaciolacustres_{}.shp'.format(feuillet))
#     path_raster_cadre = os.path.join(rep_raster_cadre, 'MNT_{}_resample.tif'.format(feuillet))
#
#     # Création du array pour la matrice
#     array_matrice_objet =matrice_confusion_objet(i, path_depot, path_raster_cadre)
#
#     # Affiche de la matrice
#     plot_matrice(array_matrice_objet, feuillet, modele, 'objet (km²)')
# #     path_out = os.path.join(rep_pred, '{}_MTM.shp'.format(name))
# #     shp = gpd.read_file(i)
#     # if feuillet == '31H02SO':
#     #     print('feuillet 31H02SO')
#     #     shp.crs = 'epsg:2950'
#     # elif feuillet == '32D02SE':
#     #     print('feuillet 32D02SE')
#     #     shp.crs = 'epsg:2952'
#     #
#     # print('sauvegarde...')
#     # shp.to_file(path_out)

# path_data = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\outputs\pixel\prediction_31H02SO_31H02_no_anth_no_anth.tif'
# output_epsg = os.path.join(os.path.dirname(path_data), 'pred_31H02SO_31H02_noAnth.tif')
# path_depot = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\inputs\depots'
# output_clip = os.path.join(os.path.dirname(path_data), 'pred_31H02SO_31H02_noAnth_clip.tif')

rep_pred = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\fichiers_outputs\pred_pixel'
rep_depot = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\inputs\depots'
liste_clip = glob.glob(os.path.join(rep_pred, '*clip.tif'))
for i in liste_clip:
    name = os.path.basename(i)
    name_split = name.split('_')
    feuillet = name_split[1]
    modele = name_split[2]
    path_depot = os.path.join(rep_depot, feuillet, 'zones_depots_glaciolacustres_{}.shp'.format(feuillet))
    array_matrice_pixel = matrice_confusion_pixel(i, path_depot)
    plot_matrice(array_matrice_pixel, feuillet, modele, 'pixel (pix)')

# feuillet = os.path.basename(path_data).split('_')[1]
# name = os.path.basename(path_data)
# mod = os.path.basename(path_data).split('_')[2][:-4]
# data = gdal.Open(path_data)
# nd = data.GetRasterBand(1).GetNoDataValue()
# data_array = data.GetRasterBand(1).ReadAsArray()
#
# mnt_resample = os.path.join(root_dir, 'Backup/MNT_{}_resample.tif'.format(feuillet))
# print(mnt_resample)
# creation_raster(data_array, mnt_resample, 'GTiff', output_epsg)
#
# clip_final(output_epsg, output_clip)
# creation_matrice_confusion(output_clip, path_depot)


