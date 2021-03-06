import geopandas as gpd
from rasterstats import zonal_stats
import os
#from osgeo import osr
from ech_pixel import creation_cadre, dissolve
from Segmentation import segmentation_main


def stats_zonales(path_metriques, path_segmentation):
    '''
    :param path_metriques: chemin du répertoire contenant les métriques sous format .tif (str)
    :param path_segmentation: chemin de la couche de segmentation sous format .shp (str)
    :return: La segmentation avec les statistiques zonales de chaque métriques pour chaque polygones (.shp)
    '''

    # On lit la couche de segmentation
    segmentation = gpd.read_file(path_segmentation)

    # Pour chaque polygones, on extrait les statistiques de chaque métriques
    for met in os.listdir(path_metriques):

        # On crée le préfixe de la colonne selon le nom de la métrique
        path = os.path.join(path_metriques, met)
        prefixe = met.split('_')[0]

        # On crée les stats zonales
        stats = zonal_stats(path_segmentation, path, stats=['min', 'max', 'median', 'mean', 'std', 'count'])
        # On formatte les statistiques pour avoir une colonne (liste) par statistique
        col = {'min': [], 'max': [], 'median': [], 'mean': [], 'std': [], 'count': []}
        for i in stats:
            col['min'].append(i['min'])
            col['max'].append(i['max'])
            col['median'].append(i['median'])
            col['mean'].append(i['mean'])
            col['std'].append(i['std'])
            col['count'].append(i['count'])

        # On ajoute les colonnes des stats dans la couche des polygones
        for c in col.keys():
            name = '{}_{}'.format(prefixe, c)
            segmentation[name] = col[c]
    return segmentation


def echantillon_objet(path_depot, segmentation):
    '''
    :param path_depot: chemin de la couche de dépôts sous format .shp (str)
    :param segmentation: chemin de la couche de segmentation sous format .shp (str)
    :return: La couche de segmentation (.shp) avec une colonne 'Zone' indiquant si le polygone est contenu (1) ou hors (0) des dépôts
    '''

    # on crée les geodataframe pour la couche de dépôts
    depot = gpd.read_file(path_depot)

    # On regroupe les polygones de la couche de dépôts
    depot_reg = dissolve(depot)

    # On peut appeler les méthodes des GeoSeries sur le geodataframe.
    # Pour within, on doit sépcifier avec quel objet de la serie on veut une comparaison.
    # Le iloc retourne une série Pandas standard, il faut donc spécifier la colonne geometry pour avoir une GeoSerie
    # https://github.com/geopandas/geopandas/issues/317

    # On crée la série booléenne pour vérifier quelles polygones sont contenus dans la zone de dépôts
    within = segmentation.within(depot_reg['geometry'].iloc[0])

    # On ajoute la série sous forme d'entier dans le geodataframe
    segmentation['Zone'] = within.astype(int)
    return segmentation


def selection_poly_cadre(path_segmentation, path_met_cadre):
    '''
    :param path_segmentation: chemin de la couche de segmentation sous format .shp (str)
    :param path_met_cadre: chemin du Raster (.tif) de référence pour créer le cadre d'échantillonnage (str)
    :return: Geodataframe des polygones de la segmentation contenus dans le cadre d'échantillonnage
    '''

    # Lecture de la couche polygonale
    seg = gpd.read_file(path_segmentation)

    # Création du cadre d'échantillonnage
    cadre, epsg, nodata = creation_cadre(path_met_cadre)

    # On sélectionne seulement les polygones à l'intérieur du cadre
    geom_cadre = cadre.loc[0, 'geometry']
    seg_cadre = gpd.GeoDataFrame(columns=['geometry'])
    seg_cadre.crs = epsg
    index = 0
    for ind, row in seg.iterrows():
        geom = row['geometry']
        if geom.within(geom_cadre):
            seg_cadre.loc[index, 'geometry'] = geom
            index += 1

    return seg_cadre


def echantillonnage_obj(path_metriques, path_met_cadre, output, path_depot=None, path_segmentation=None,
                        input_met=None, markers=None, compactness=None, output_segmentation=None):
    '''
    :param path_metriques: Chemin du répertoire contenant les métriques (.tif) pour calculer les statistiques (str)
    :param path_met_cadre: chemin du Raster de référence pour créer le cadre d'échantillonnage (str)
    :param path_segmentation: Chemin du fichier .shp de la segmentation (str)
    :param output: Chemin du fichier de sortie (str)
    :param path_depot: Chemin de la couche de dépôts (.shp) pour identifier les polygones in/ext des dépôts
                       Si laissé par défaut, seules les statistiques de zones seront créées sans la colonne Zone.
    :param input_met: Chemin du fichier .tif utilisé pour faire la segmentation (str)
    :param markers: Nombre de polygone voulu dans la segmentation (int)
    :param compactness: Influence la forme des polygones, ex: 0.02 (float)
    :param output_segmentation: Chemin du fichier de sortie .shp de la segmentation à créer (str)
    :return: Couche polygonale de segmentation incluant les statistiques de zones pour chaque métriques contenues dans
             le répertoire 'path_métriques'.
    '''

    # Si aucune segmentation n'est specifiée, on la crée
    if path_segmentation is None:
        segmentation_main(input_met, markers, compactness, output_segmentation)
        path_segmentation = output_segmentation

    # Sélection des polygones à l'intérieur de la superficie d'échantillonnage
    print("Sélection des polygones à l'intérieur du cadre...")
    path_seg_cadre = "/vsimem/seg_cadre.shp"
    seg_cadre = selection_poly_cadre(path_segmentation, path_met_cadre)
    seg_cadre.to_file(path_seg_cadre)

    # Statistiques zonales
    print('Calcul des statistiques zonales...')
    seg_stats = stats_zonales(path_metriques=path_metriques, path_segmentation=path_seg_cadre)

    # Échantillonnage si spécifié
    if path_depot is not None:
        print('Échantillonnage...')
        seg_stats_ech = echantillon_objet(path_depot=path_depot, segmentation=seg_stats)

        # On sauvegarde la couche de segmentation avec la colonne des zones et les stats zonales
        print('Sauvegarde...')
        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(os.path.dirname(output))
        seg_stats_ech.to_file(output)
    else:
        # On sauvegarde la couche de segmentation seulement avec les stats zonales
        print('Sauvegarde...')
        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(os.path.dirname(output))
        seg_stats.to_file(output)

    print('Terminé')


# #### INITIATION DU SCRIPT ####
if __name__ == "__main__":
    # path_segmentation = r'E:\OneDrive - USherbrooke\001 APP\Programmation\inputs\segmentations\seg_31H02SE_sickit_v5000_0_02.shp'
    path_segmentation = os.path.join(root_dir, 'inputs/segmentations/seg_stats_{}_v2.shp'.format(i))
    # path_metriques = r'E:\OneDrive - USherbrooke\001 APP\Programmation\inputs\tiffs\31H02SE'
    path_metriques = os.path.join(root_dir, 'inputs/tiffs/{}'.format(i))
    # path_met_cadre = r'E:\OneDrive - USherbrooke\001 APP\Programmation\inputs\MNT\resample\31H02\MNT_31H02SE_resample.tif'
    path_met_cadre = os.path.join(root_dir, 'inputs/MNT/resample/{}/MNT_{}_resample.tif'.format(i[:-2], i))
    # path_depot = r'E:\OneDrive - USherbrooke\001 APP\Programmation\inputs\depots\31H02SE\zones_depots_glaciolacustres_31H02SE.shp'
    path_depot = os.path.join(root_dir, 'inputs/depots/{}/zones_depots_glaciolacustres_{}.shp'.format(i, i))

    echantillonnage_obj(path_metriques=path_metriques, path_met_cadre=path_met_cadre,
                        path_segmentation=path_segmentation, path_depot=path_depot,
                        output=path_segmentation)




