import numpy as np
import os
from tifffile import imread

tifs_dir = r'E:\OneDrive - USherbrooke\001 APP\Projet_session_geoinfo\data'

# Import des images en matrices numpy
image1 = imread(os.path.join(tifs_dir, 'Pente_WB_31H02SE.tif'))
image2 = imread(os.path.join(tifs_dir, 'RelTPI_WB_31H02SE.tif'))
image3 = imread(os.path.join(tifs_dir, 'TWI_WB_31H02SE.tif'))

image_list = [image1, image2, image3]

# Vérifier si les images sont tous de la même forme (shape)
shapeimg1 = image1.shape
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
for i in range(m_cols - 1):
    for j in range(n_rows - 1):
        print(image1[i][j])




