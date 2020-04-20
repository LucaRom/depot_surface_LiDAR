depot = QgsProject.instance().mapLayersByName('depot_NESE')[0]
seg = QgsProject.instance().mapLayersByName('seg_NESE')[0]

# Fonction pour calculer la superficie projetée
lyr_crs = depot.crs()
#epsg = str(lyr_crs).split(' ')[1].split(':')[1][:-1]

elps_crs = QgsCoordinateReferenceSystem()
elps_crs.createFromUserInput('GRS80')

trans_context = QgsCoordinateTransformContext()
trans_context.calculateDatumTransforms(lyr_crs, elps_crs)

area = QgsDistanceArea()
area.setEllipsoid('GRS80')
area.setSourceCrs(lyr_crs, trans_context)


coucheIn = processing.run('native:clip', {'INPUT': seg, 'OUTPUT': 'memory:', 'OVERLAY':depot})['OUTPUT']
QgsProject.instance().addMapLayer(coucheIn)

coucheOut = processing.run('native:difference', {'INPUT': seg, 'OUTPUT': 'memory:', 'OVERLAY':depot})['OUTPUT']
QgsProject.instance().addMapLayer(coucheIn)


areaIn1 = 0
areaIn0 = 0
for f in coucheIn.getFeatures():
    geom = f.geometry()
    if f['zone'] == 0:
        areaIn0 = areaIn0 + area.measureArea(geom)
    elif f['zone'] == 1:
        areaIn1 = areaIn1 + area.measureArea(geom)

areaOut1 = 0
areaOut0 = 0
for f in coucheOut.getFeatures():
    geom = f.geometry()
    if f['prediction'] == 0:
        areaOut0 = areaOut0 + area.measureArea(geom)
    elif f['prediction'] == 1:
        areaOut1 = areaOut1 + area.measureArea(geom)


areaTotal = 0
for feature in seg.getFeatures():
    geo = feature.geometry()
    areaTotal = areaTotal + area.measureArea(geo)

accuracy = ((areaIn1 + areaOut0)/areaTotal) * 100


print('areaIn1: {}'.format(areaIn1))
print('areaIn0: {}'.format(areaIn0))
print('areaOut1: {}'.format(areaOut1))
print('areaOut0: {}'.format(areaOut0))
print('areaTotal: {}'.format(areaTotal))
print('accuracy: {}'.format(accuracy))
