import geopandas as gpd
from rasterstats import zonal_stats
from datetime import datetime
import os
from osgeo import osr
from ech_pixel import creation_cadre

#### DÉFINITION DES FONCTIONS ####

#Regrouper les polygones d'une couche en 1 multipolygone
def dissolve(geodataframe):
    if len(geodataframe) > 1:
        diss = geodataframe.unary_union
        shpDiss = gpd.GeoDataFrame(columns=['geometry'])
        shpDiss.loc[0, 'geometry'] = diss
        return shpDiss
    return geodataframe


# # Import de tous les shapefiles d'un dossier et on les regroupe dans un seul fichier
# def set_root_chm():
#     # On définit le dossier parent pour le réutiliser dans l'import d'intrants
#     global root_dir
#     root_dir = os.path.abspath(os.path.dirname(__file__))
#
#     return root_dir

# def import_merge_seg():
#     # Chemin vers le dossier avec les shapefiles
#     folder_path = os.path.join(root_dir, 'inputs/segmentations/seg_Scikit_mai2020_31H02_NE_SE')
#
#     # On crée la liste des shapefiles
#     files = os.listdir(folder_path)  # Liste des fichiers dans le dossier "folder"
#     shp_list = [os.path.join(folder_path, i) for i in files if i.endswith('.shp')]  # Obtenir une liste des chemins pour
#                                                                                     # .shp seulement
#     # On join les fichiers .shp de la liste
#     new_shp_temp = gpd.GeoDataFrame(pd.concat([gpd.read_file(i) for i in shp_list],
#                                               ignore_index=True), crs=gpd.read_file(shp_list[0]).crs)
#
#     return new_shp_temp # Retourne le shapefile

# def set_chemins():
#
#     global path_segmentation
#     global path_depot
#     global path_met
#     global output
#
#     # On ajoute la date au fichier sortant pour suivre nos tests
#     date_classi = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
#
#     #Chemins de la couche de segmentation et de la couche de dépôts
#     path_segmentation = os.path.join(root_dir, 'inputs/segmentations/seg_ecognition_31h02NE_SE/Test2_NE_Clip.shp')
#     path_depot = os.path.join(root_dir, 'inputs/depots/31H02NE/zones_depots_glaciolacustres_31H02NE_MTM8.shp')
#
#     # Chemin du répertoire contenant les métriques
#     path_met = os.path.join(root_dir, 'inputs/tiffs/31H02NE_5m/')
#
#     # path_segmentation = os.path.join(root_dir, 'inputs/segmentations/seg_ecognition_31h02NE_SE/Test2_SE_Clip.shp')
#     # path_depot = os.path.join(root_dir, 'inputs/depots/31H02SE/zones_depots_glaciolacustres_31H02SE_MTM8.shp')
#     #
#     # # Chemin du répertoire contenant les métriques
#     # path_met = os.path.join(root_dir, 'inputs/tiffs/31H02SE_5m/')
#
#     # chemin de la couche de sortie
#     nom_fichier = 'result_prediction_SEG_ecognition_NE' + date_classi + '.shp'
#     output = os.path.join(root_dir, 'outputs/Segmentations', nom_fichier)

def stats_zonales(path_metriques, path_segmentation):

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

    # Lecture de la couche polygonale
    seg = gpd.read_file(path_segmentation)

    # Création du cadre d'échantillonnage
    cadre, epsg = creation_cadre(path_met_cadre)

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


def echantillonnage_obj(path_metriques, path_met_cadre, path_segmentation, path_depot, output):

    # Sélection des polygones à l'intérieur de la superficie d'échantillonnage
    print("Sélection des polygones à l'intérieur du cadre...")
    path_seg_cadre = "/vsimem/seg_cadre.shp"
    seg_cadre = selection_poly_cadre(path_segmentation, path_met_cadre)
    seg_cadre.to_file(path_seg_cadre)

    # Statistiques zonales
    print('Calcul des statistiques zonales...')
    seg_stats = stats_zonales(path_metriques=path_metriques, path_segmentation=path_seg_cadre)

    # Échantillonnage
    print('Échantillonnage...')
    seg_stats_ech = echantillon_objet(path_depot=path_depot, segmentation=seg_stats)

    # On sauvegarde la couche de segmentation avec la colonne des zones et les stats zonales
    print('Sauvegarde...')
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))
    seg_stats_ech.to_file(output)
    print('Terminé')


# #### INITIATION DU SCRIPT ####
if __name__ == "__main__":

    path_segmentation = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\inputs\segmentations\segmentation_31H02SO.shp'
    path_metriques = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\inputs\tiffs\31H02SO'
    path_met_cadre = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\inputs\MNT\resample\MNT_31H02SO_resample.tif'
    path_depot = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\inputs\depots\31H02SO\zones_depots_glaciolacustres_31H02S0.shp'

    echantillonnage_obj(path_metriques=path_metriques, path_met_cadre=path_met_cadre,
                        path_segmentation=path_segmentation, path_depot=path_depot,
                        output=path_segmentation)




