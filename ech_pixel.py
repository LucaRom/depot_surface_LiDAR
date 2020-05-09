import geopandas as gpd
import random
from fiona.crs import from_epsg
from shapely.geometry import shape, Point
from shapely.ops import nearest_points

#path = r'C:\Users\home\Documents\Documents\APP2\polygon_test.shp'
path = r'C:\Users\home\Documents\Documents\APP2\depots_31H02\zone_depots_glaciolacustre_31H02NE_MTM8_reg.shp'
value = 2000
minDistance = 500


def check_min_distance(point, distance, points):
    """Check if distance from given point to all other points is greater
    than given value.
    """
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

poly = gpd.read_file(path)
epsg = int(poly.crs['init'].split(':')[1])
sample = gpd.GeoDataFrame()
sample['geometry'] = None
sample['id'] = None
sample.crs = from_epsg(epsg)

total = 100.0 / len(poly) if len(poly) else 0
for ind, row in poly.iterrows():
    geom = row['geometry']
    bbox = shape(geom).bounds
    # if minDistance:
    #     index = sample.sindex
    # points = dict()
    nPoints = 0
    nIterations = 0
    maxIterations = value * 50
    feature_total = total / value if value else 1

    random.seed()
    pointId = 0
    while nIterations < maxIterations and nPoints < value:

        height = bbox[3] - bbox[1]
        width = bbox[2] - bbox[0]
        rx = bbox[0] + width * random.random()
        ry = bbox[1] + height * random.random()

        p = Point(rx, ry)
        # geom = QgsGeometry.fromPointXY(p)
        if p.within(geom) and \
                (not minDistance or check_min_distance(p, minDistance, sample)):
            sample.loc[nPoints, 'geometry'] = p
            sample.loc[nPoints, 'id'] = pointId
            print(sample)

            # f = QgsFeature(nPoints)
            # f.initAttributes(1)
            # f.setFields(fields)
            # f.setAttribute('id', pointId)
            # f.setGeometry(geom)
            # sink.addFeature(f, QgsFeatureSink.FastInsert)
            # points[nPoints] = p
            nPoints += 1
            pointId += 1
            # feedback.setProgress(current_progress + int(nPoints * feature_total))
        nIterations += 1

        if nPoints < value:
            print('Could not generate requested number of random points. Maximum number of attempts exceeded.')

sample.to_file(r'C:\Users\home\Documents\Documents\APP3\test_points.shp')


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

