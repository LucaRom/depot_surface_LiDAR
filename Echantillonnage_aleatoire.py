''' Échantillonnage aléatoire, David Ethier 2020'''
'''
Produit une couche de points échantillons à l'intérieur et extérieur des zone de dépôts de la couche en entrée
Le nombre de points et la distance minimale (unité du projet) sont spécifiées par l'utilisateur


Upgrade possible => Avoir toutes les couche en mémoire, aucune sur le disque, pas besoin de temp
                    Le Polygonize de GDAL et RasterCalculator créent des couches sur le disque.
'''
import processing
import os
import subprocess
import shutil

# Définition des intrants
path_MNT = r'C:\Users\home\Documents\Documents\APP2\MNT_31H02NE_5x5.tif'
path_depot = r'C:\Users\home\Documents\Documents\APP2\depots_31H02NE\zone_depots_glaciolacustre_31H02NE_MTM8_reg.shp'
path_output = r'C:\Users\home\Documents\Documents\APP2\Ech_31H02NE.shp'
path_temp = r'C:\temp_echan'
distance_min = 1000
nb_points = 2000

    
# Création du répertoire temporaire
#path_temp = os.path.join(os.path.dirname(path_MNT), 'temp_echan')
if not os.path.exists(path_temp):
    os.mkdir(path_temp)

# Importation des couches
mnt = QgsRasterLayer(path_MNT, 'MNT')
depot = QgsVectorLayer(path_depot, 'depots', 'ogr')

# Regrouper couche de dépôts
if depot.featureCount() > 1:
    diss = processing.run('native:dissolve', {'INPUT': depot, 'OUTPUT': 'memory:'})['OUTPUT']
    depot =  processing.run('native:fixgeometries', {'INPUT': diss, 'OUTPUT': 'memory:'})['OUTPUT']

#QgsProject.instance().addMapLayers([depot])

# Multiplier MNT par 0
mnt0_path = os.path.join(path_temp, 'mnt0.tif')
entries = []
ras = QgsRasterCalculatorEntry()
ras.ref = 'ras@1'
ras.raster = mnt
ras.bandNumber = 1
entries.append(ras)

calc = QgsRasterCalculator('ras@1 = 0', mnt0_path, 'GTiff', mnt.extent(), mnt.width(), mnt.height(), entries)
calc.processCalculation()
mnt0 = QgsRasterLayer(mnt0_path, 'mnt0')
#QgsProject.instance().addMapLayer(mnt0)

# Polygoniser le MNT
path_polyMnt = os.path.join(path_temp, 'Polymnt0.shp')
polygonize = processing.run('gdal:polygonize', {'INPUT': mnt0, 'BAND':1, 'FIELD': 'DN', 'OUTPUT': path_polyMnt})['OUTPUT']
polyMntBrise = QgsVectorLayer(path_polyMnt, 'polyMntBrise')
polyMnt = processing.run('native:fixgeometries', {'INPUT': polyMntBrise, 'OUTPUT': 'memory:'})['OUTPUT']
#QgsProject.instance().addMapLayer(polyMnt)

# Création buffer depots 
buffDepots = processing.run('native:buffer', {'INPUT': depot, 'DISTANCE': distance_min, 'SEGMENTS': 5, 'END_CAP_STYLE': 0, 'JOIN_STYLE': 0, 'OUTPUT': 'memory:'})['OUTPUT'] 
#QgsProject.instance().addMapLayer(buffDepots)

# Clip du buffer au extent du MNT
buffclip = processing.run('native:clip', {'INPUT': buffDepots, 'OVERLAY': polyMnt, 'OUTPUT': 'memory:'})['OUTPUT']
#QgsProject.instance().addMapLayer(buffclip)

# Création de la zone ext
zoneExtMulti = processing.run('native:difference', {'INPUT': polyMnt, 'OVERLAY': buffclip, 'OUTPUT': 'memory:'})['OUTPUT']
zoneExt = processing.run('native:dissolve', {'INPUT': zoneExtMulti, 'OUTPUT': 'memory:'})['OUTPUT']
#QgsProject.instance().addMapLayer(zoneExt)

# Création des points aléatoires intérieurs
pointInt = processing.run('qgis:randompointsinsidepolygons', {'INPUT': depot, 'STRATEGY': 0, 'VALUE': nb_points, 'MIN_DISTANCE': distance_min, 'OUTPUT': 'memory:'})['OUTPUT']
#QgsProject.instance().addMapLayer(pointInt)

# Création des points aléatoires extérieurs
nbPoints = pointInt.featureCount()
pointExt = processing.run('qgis:randompointsinsidepolygons', {'INPUT': zoneExt, 'STRATEGY': 0, 'VALUE': nbPoints, 'MIN_DISTANCE': distance_min, 'OUTPUT': 'memory:'})['OUTPUT']
#QgsProject.instance().addMapLayer(pointExt)

# Création du champs 'zone'
intPr = pointInt.dataProvider()
extPr = pointExt.dataProvider()

intPr.addAttributes([QgsField('Zone', QVariant.Int)])
extPr.addAttributes([QgsField('Zone', QVariant.Int)])
pointInt.updateFields()
pointExt.updateFields()

for inFeat in pointInt.getFeatures():
    att = {1: 1}
    intPr.changeAttributeValues({inFeat.id(): att})

for extFeat in pointExt.getFeatures():
    att = {1: 0}
    extPr.changeAttributeValues({extFeat.id(): att})
    
#QgsProject.instance().addMapLayer(pointInt)
#QgsProject.instance().addMapLayer(pointExt)

# Fusion des couches de points + sauvegarde
pointsTotal = processing.run('native:mergevectorlayers', {'LAYERS': [pointInt, pointExt], 'CRS': pointInt.crs(), 'OUTPUT': path_output})['OUTPUT']
#QgsProject.instance().addMapLayer(pointsTotal)

# Supression des fichiers temporaires, fonctionne pas

#del path_MNT
#del path_polyMnt
#del path_depot
#del depot
#del mnt
#del polyMnt
#del mnt0
#del mnt0_path
#del buffDepots
#del buffclip
#del zoneExtMulti
#del zoneExt
#del pointInt
#del nbPoints
#del pointExt
#del intPr
#del extPr
#del pointsTotal
#sys.exit
#for file in os.listdir(path_temp):
#    path_file = os.path.join(path_temp, file)
#    os.remove(path_file)
#os.rmdir(path_temp)
#
# Fin
print('Couche échantillons produite \nNombre de points : {}'.format(nbPoints))











