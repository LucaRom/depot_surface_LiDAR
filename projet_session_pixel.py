import numpy as np
import os
from tifffile import imread

# On importe le modèle de classification fait auparavant
''' À Compléter'''

# On définit le dossier parent pour le réutiliser dans l'import d'intrants
root_dir  = os.path.dirname("__file__")
filename = os.path.join(root_dir, 'path/where/to/go')

# Import des images en matrices numpy
tiffs_path = os.path.join(root_dir, 'inputs/tiffs/') # Définition du chemin pour les images
metric1 = imread(os.path.join(tiffs_path, 'AvrNorVecAngDev_WB_31H02NE.tif'))
metric2 = imread(os.path.join(tiffs_path, 'CirVarAsp_WB_31H02NE.tif'))
metric3 = imread(os.path.join(tiffs_path, 'DownslopeInd_WB_31H02NE.tif'))
metric4 = imread(os.path.join(tiffs_path, 'EdgeDens_WB_31H02NE.tif'))
metric5 = imread(os.path.join(tiffs_path, 'Pente_WB_31H02NE.tif'))
metric6 = imread(os.path.join(tiffs_path, 'PlanCur_WB_31H02NE.tif'))
metric7 = imread(os.path.join(tiffs_path, 'ProfCur_WB_31H02NE.tif'))
metric8 = imread(os.path.join(tiffs_path, 'RelTPI_WB_31H02NE.tif'))
metric9 = imread(os.path.join(tiffs_path, 'SphStdDevNor_WB_31H02NE.tif'))
metric10 = imread(os.path.join(tiffs_path, 'tanCur_WB_31H02NE.tif'))
metric11 = imread(os.path.join(tiffs_path, 'TWI_WB_31H02NE.tif'))

print(metric1, metric2, metric3)

# On crée la liste des metrics pour les itérer
image_list = [metric1, metric2, metric3, metric4, metric5, metric6, metric7, metric8, metric9, metric10, metric11]

# Vérifier si les images sont tous de la même forme (shape)
shapeimg1 = metric1.shape
for i in image_list:
    if i.shape != shapeimg1:
        print("Les images ne sont pas de la même taille")
        print(i)
        break
    else:
        print("Ok!")

# On extrait les dimensions des images
n_rows = shapeimg1[0]
m_cols = shapeimg1[1]

# On itere les valeurs des images pour chaque pixel
#for i in range(m_cols - 1):
for i in range(800, 810):
    dict_pixel = dict()
    #for j in range(n_rows - 1):
    for j in range(800, 810):
        dict_pixel['metric1'] = metric1[i][j]
        dict_pixel['metric2'] = metric2[i][j]
        dict_pixel['metric3'] = metric3[i][j]
        dict_pixel['metric4'] = metric4[i][j]
        dict_pixel['metric5'] = metric5[i][j]
        dict_pixel['metric6'] = metric6[i][j]
        dict_pixel['metric7'] = metric7[i][j]
    print(dict_pixel)




