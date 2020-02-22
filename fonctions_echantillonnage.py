import rasterio
import fiona
import rasterio.mask
import matplotlib.pyplot as plt
import whitebox
import os
import math
import numpy as np

def enregistrement_masque(masque_ext_array, masque_zone_array, out_meta, out_transform_ext, out_transform_zones,
                          dossier_output):
    # Liste des array des masques avec leur out_transform correspondant
    liste_masque = [[masque_ext_array, out_transform_ext], [masque_zone_array, out_transform_zones]]

    liste_path = []
    suffixe = ''

    # Sauvegarde de chaque masque de la liste sous format .tif dans le répertoire en entrée
    for i in range(len(liste_masque)):

        masque = liste_masque[i][0]
        out_transform = liste_masque[i][1]

        if i == 0:
            suffixe = 'ext'
        elif i == 1:
            suffixe = 'zones'

        out_meta.update({"driver": "GTiff",
                         "height": masque.shape[1],
                         "width": masque.shape[2],
                         "transform": out_transform})

        fichier = os.path.join(dossier_output, 'masque_{}.tif'.format(suffixe))
        liste_path.append(fichier)
        with rasterio.open(fichier, "w", **out_meta) as dest:
            dest.write(masque)

    return liste_path


def creation_masque(path_couche_depot, path_metrique, dossier_output):

    # Création des masques des zones de dépôts et extérieur aux zones
    with fiona.open(path_couche_depot, 'r') as shapefile:
        polygones = [feature['geometry'] for feature in shapefile]

    with rasterio.open(path_metrique) as metrique:
        masque_ext_array, out_transform_ext = rasterio.mask.mask(metrique, polygones, crop=True)

        masque_zones_array, out_transform_zones = rasterio.mask.mask(metrique, polygones, crop=False, invert=True)
        out_meta = metrique.meta

    # Enregistrement en raster dans le dossier temporaire
    paths = enregistrement_masque(masque_ext_array, masque_zones_array, out_meta, out_transform_ext, out_transform_zones,
                          dossier_output)

    return paths


def echantillonnage(masque_ext, masque_zone, dossier_output, path_metrique):

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False

    liste_raster = [masque_ext, masque_zone]
    liste_valeur_in = []
    liste_valeur_out = []

    # Pour chaque masque de la liste
    for raster in liste_raster:

        suffixe = ''
        if raster == liste_raster[0]:
            suffixe = 'in'
        elif raster == liste_raster[1]:
            suffixe = 'out'

        # Création du raster d'échantillons aléatoire sur le masque
        random_raster = os.path.join(dossier_output, 'random_values_{}.tif'.format(suffixe))
        wbt.random_sample(raster, random_raster, 2000)

        # Transformation du raster d'échantillon en points
        random_point = os.path.join(dossier_output, 'random_values_{}.shp'.format(suffixe))
        wbt.raster_to_vector_points(random_raster, random_point)

        # Extraction des valeurs de la métrique à la localisation de chaque point. Les valeurs sont stockées dans
        # un nouvel attribut de la couche
        wbt.extract_raster_values_at_points(path_metrique, random_point, out_text=False)

        # Extraction et formatage des valeurs dans un dictionnaire. La clé 'in_zone' contient la liste des valeurs
        # à l'intérieur des zones. La clé 'out_zone' contient la liste des valeurs à l'extérieur des zones.
        with fiona.open(os.path.join(dossier_output, 'random_values_{}.shp'.format(suffixe)), 'r') as points:
            for feature in points:
                for key, value in feature.items():
                    if key == 'properties':
                        if raster == liste_raster[0]:
                            liste_valeur_in.append(value['VALUE1'])
                        elif raster == liste_raster[1]:
                            liste_valeur_out.append(value['VALUE1'])

    dict_valeurs = {'in_zone':liste_valeur_in, 'out_zone': liste_valeur_out}
    return dict_valeurs


def round_decade_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


def get_max_freq(dic, key):
    max_X = None
    max_Y = None

    other_key = ''
    if key == 'in_zone':
        other_key = 'out_zone'
    elif key == 'out_zone':
        other_key = 'in_zone'

    # définition de l'histogramme
    n_1 = plt.hist(x=dic[key], bins='auto', color='#0504aa', alpha=0.7, rwidth=0.85)
    n_2 = plt.hist(x=dic[other_key], bins='auto', color='#0504aa', alpha=0.7, rwidth=0.85)

    # Valeur max en X
    liste_max_X = [max(dic[key]), max(dic[other_key])]
    liste_min_X = [min(dic[key]), min(dic[other_key])]
    max_X = int(max(liste_max_X))
    min_X = int(min(liste_min_X))

    # Valeur max en Y
    maxfreq1 = n_1[0].max()
    maxfreq2 = n_2[0].max()
    liste_maxfreq = [maxfreq1, maxfreq2]
    max_Y = int(max(liste_maxfreq))

    plt.cla()

    return [min_X, max_X, max_Y]


def histogramme(dic, key, metrique, feuillet, output):

    maxs = get_max_freq(dic, key)
    xmin = round(maxs[0])
    xmax = int(round_decade_up(maxs[1], -1))
    ymax = int(round_decade_up(maxs[2], -1))

    if key == 'in_zone':
        plt.title("{} à l'intérieur des zones de dépôts, {}".format(metrique, feuillet))
    elif key == 'out_zone':
        plt.title("{} à l'extérieur des zones de dépôts, {}".format(metrique, feuillet))

    # définition de l'histogramme
    n_3, bins_3, patches_3 = plt.hist(x=dic[key], bins='auto', color='#0504aa', alpha=0.7, rwidth=0.85)

    # définition du min et max de l'axe des X
    # plt.xlim((xmin, xmax))

    # définition du min et max de l'axe des Y
    plt.ylim((0, ymax))

    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Valeurs des échantillons')
    plt.ylabel('Fréquence')
    plt.savefig(os.path.join(output, '{}_{}_{}.png'.format(metrique, key, feuillet)))

    plt.show()


