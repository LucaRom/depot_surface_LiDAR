import geopandas as gpd
import random
from fiona.crs import from_epsg
from shapely.geometry import shape, Point
from shapely.ops import nearest_points
import shapely.speedups

#@profile
def check_min_distance(point, distance, points):

    if distance == 0:
        return True
    if len(points) > 0:
        uni = points.unary_union
        nearest = nearest_points(point, uni)
        if len(nearest) == 0:
            return True
        if nearest[1].distance(point) < distance:
            return False
    return True


#@profile
def echantillon_pixel(input, minDistance, value, output):

    poly = gpd.read_file(input)
    epsg = int(poly.crs['init'].split(':')[1])
    sample = gpd.GeoDataFrame(columns=['geometry', 'id'])
    sample.crs = from_epsg(epsg)

    for ind, row in poly.iterrows():
        geom = row['geometry']
        bbox = shape(geom).bounds
        index = sample.sindex
        nPoints = 0
        nIterations = 0
        maxIterations = value * 5

        random.seed()
        pointId = 0
        while nIterations < maxIterations and nPoints < value:

            height = bbox[3] - bbox[1]
            width = bbox[2] - bbox[0]
            rx = bbox[0] + width * random.random()
            ry = bbox[1] + height * random.random()

            p = Point(rx, ry)

            if p.within(geom) and (not minDistance or check_min_distance(p, minDistance, sample)):
                    sample.loc[nPoints, 'geometry'] = p
                    sample.loc[nPoints, 'id'] = pointId
                    nPoints += 1
                    pointId += 1
            nIterations += 1
            if nIterations % 1000 == 0:
                print(nIterations)

        if nPoints < value:
            print(sample)
            print('Could not generate requested number of random points. Maximum number of attempts exceeded.')

    sample.to_file(output)

#@profile
def main():

    shapely.speedups.enable()
    # Path de la couche à échantillonner
    path = r'C:\Users\home\Documents\Documents\APP2\depots_31H02\zone_depots_glaciolacustre_31H02NE_MTM8_reg.shp'
    # Nombre de points
    value = 2000
    # Distance minimale en unité du système de la couche
    minDistance = 500
    # Path de sauvegarde de l'échantillonnage
    output = r'C:\Users\home\Documents\Documents\APP3\test_points.shp'
    # Échantillonnage
    #echantillon_pixel(input=path, minDistance=minDistance, value=value, output=output)

    shp = gpd.read_file(path)
    print(shp.loc[0, 'geometry'])


if __name__ == "__main__":
    main()



# orig = Point(1, 1.67)
# origin = gpd.GeoDataFrame()
# origin['geometry'] = None
# origin.loc[0, 'geometry'] = orig
#
# destin = gpd.GeoDataFrame()
# destin['geometry'] = None
# liste_point = [Point(1, 1.45), Point(2, 2), Point(0, 2.5)]
# for i in range(3):
#     destin.loc[i, 'geometry'] = liste_point[i]
#
# union = destin.unary_union
# print(union)
# near = nearest_points(orig, union)
# print(list(near)[1])
# print(near[1].distance(orig))

