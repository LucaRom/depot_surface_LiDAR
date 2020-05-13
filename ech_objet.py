import geopandas as gpd
from rasterstats import zonal_stats
import os


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

    # On peut appeler les méthodes des GeoSeries sur le geodataframe.
    # Pour within, on doit sépcifier avec quel objet de la serie on veut une comparaison.
    # Le iloc retourne une série Pandas standard, il faut donc spécifier la colonne geometry pour avoir une GeoSerie
    # https://github.com/geopandas/geopandas/issues/317

    # On crée la série booléenne pour vérifier quelles polygones sont contenus dans la zone de dépôts
    within = segmentation.within(depot['geometry'].iloc[0])

    # On ajoute la série sous forme d'entier dans le geodataframe
    segmentation['Zone'] = within.astype(int)
    return segmentation


def main():

    # Chemins de la couche de segmentation et de la couche de dépôts
    path_segmentation = r'C:\Users\home\Documents\Documents\APP2\polygon_test.shp'
    path_depot = r'C:\Users\home\Documents\Documents\APP2\Depots_31H\Depots_31H\zone_depots_glaciolacustre_31H02NE_MTM8_reg.shp'

    # Chemin du répertoire contenant les métriques
    path_met = r'C:\Users\home\Documents\Documents\APP2\Metriques\31H02\31H02NE'

    # chemin de la couche de sortie
    output = r'C:\Users\home\Documents\Documents\APP2\polygon_test.shp'

    # Statistiques zonales
    print('Calcul des statistiques zonales...')
    seg_stats = stats_zonales(path_metriques=path_met, path_segmentation=path_segmentation)

    # Échantillonnage
    print('Échantillonnage...')
    seg_stats_ech = echantillon_objet(path_depot=path_depot, segmentation=seg_stats)

    # On sauvegarde la couche de segmentation avec la colonne des zones et les stats zonales
    print('Sauvegarde...')
    seg_stats_ech.to_file(output)
    print('Terminé')


if __name__ == "__main__":
    main()




