import rasterio
import fiona
import rasterio.mask
import matplotlib.pyplot as plt
import random
import whitebox
import os
import numpy as np
import math




def round_decade_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier




# with rasterio.open(path) as metrique:
#     image = metrique.read(1, out_shape=(1, metrique.height, metrique.width))
#
#     for ligne in image:
#         print(ligne)
#     print()

# Échantillonnage aléatoire stratifié systématique

# liste = []
# liste_choix = []
# taille = 20
# index_col = 0
# index_ligne = 0
#
# # On parcours la grille le nombre de fois que la fenêtre choisie rentre
# for j in range(int(metrique.height/taille)):
#     for i in range(int(metrique.width/taille)):
#
#         # On défini un range de ligne et de colonne correspondant à la taille de la grille en partant d'en haut à gauche
#         for ligne in range(index_ligne, index_ligne + taille):
#             for indexes in range(index_col, index_col + taille):
#                 # Pour chaque pixel dans la fenêtre définie, on l'ajoute dans une liste
#                 liste.append(image[ligne][indexes])
#         else:
#             # Une fois tous les pixels de la fenêtre dans la liste, on en choisit 1 au hasard qu'on ajoute à la liste de tous les pixels choisis
#             print(liste)
#             choix = random.choice(liste)
#             liste_choix.append(choix)
#
#             # S'il reste encore assez de ligne à la grille, on se déplace d'une taille de fenêtre vers le bas jusqu'à la fin de la grille
#             if metrique.height >= (index_ligne + taille):
#                 index_ligne += taille
#                 liste = []
#     else:
#         # Si on a atteint le nombre max de ligne pour descendre,
#         # S'il reste assez de colonne dans la grille, on recommence le processus, mais 1 taille de fenêtre plus à droite jusqua'à la fin de la grille
#         if metrique.width >= (index_col + taille):
#             index_col += taille
#             index_ligne = 0
#
# print(liste_choix)
# #