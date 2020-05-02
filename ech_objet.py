import geopandas as gpd
from rasterstats import zonal_stats


# # ECHANTILLONNAGE
# path_poly = r'C:\Users\home\Documents\Documents\APP2\polygon_test.shp'
# path_depot = r'C:\Users\home\Documents\Documents\APP2\Depots_31H\Depots_31H\zone_depots_glaciolacustre_31H02NE_MTM8_reg.shp'
#
# # on crée les geodataframe pour les couches
# poly = gpd.read_file(path_poly)
# depot = gpd.read_file(path_depot)
#
# # On peut appeler les méthodes des GeoSeries sur le geodataframe.
# # Pour intersects, on doit sépcifier avec quel objet de la serie on veut une comparaison.
# # Le iloc retourne une série Pandas standard, il faut donc spécifier la colonne geometry pour avoir une GeoSerie
# # https://github.com/geopandas/geopandas/issues/317
#
# #print(poly.intersects(depot['geometry'].iloc[0]))
#
# # On crée la série booléenne pour vérifier quelles polygones sont contenus dans la zone de dépôts
# within = poly.within(depot['geometry'].iloc[0])
#
# # On ajoute la série sous forme d'entier dans le geodataframe
# poly['Zone'] = within.astype(int)
# print(poly)


# STATISTIQUES ZONALES

path_met = r'C:\Users\home\Documents\Documents\APP2\Metriques\31H02\31H02NE\Pente_WB_31H02NE.tif'
path_shp = r'C:\Users\home\Documents\Documents\APP2\polygon_test.shp'

stats = zonal_stats(path_shp, path_met, stats=['min', 'max', 'median', 'mean', 'std', 'sum'])
for i in stats:
    print(i)

