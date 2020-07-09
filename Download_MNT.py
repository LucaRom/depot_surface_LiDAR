'''
David Ethier, Yves Voirin,  2020
'''

import os
from ftplib import FTP
import geopandas as gpd


def selection_mnt(feuillet, path_index, col_feuillet):
    '''
    :param feuillet: numéro du feuillet sélectionné ex: '31H02NE' (str)
    :param path_index: chemin de la couche .shp de l'index des feuillets couverts par le LiDAR (forêt ouverte),
           découpage 1/20 000
    :param col_feuillet: Titre de la colonne qui comporte le numéro des feuillets dans la couche index (str)
    :return: Une liste des feuillets à télécharger. Les 8 feuillets adjacents et le feuillet sélectionné sont ajoutés
             à la liste pour créer une mosaique, qui permettra de créer un buffer
    '''
    # Lecture de la couche index
    index = gpd.read_file(path_index)
    # Extraction du géom du feuillet sélectionné
    geom_feuillet = index['geometry'][index[col_feuillet] == feuillet].values[0]
    # On vérifie quels feuillets sont adjacents et on ajoute leur numéro à la liste à télécharger
    index['intersect'] = index.intersects(geom_feuillet)
    liste_download = (list(index[col_feuillet][index['intersect'] == True].values))
    return liste_download


def download_ftp(ftpparent, ftpdirectory, liste_files, rep_output):
    '''
    :param ftpparent: Répertoire de base dans lequel se trouve les fichiers à télécharger (str)
    :param ftpdirectory: adresse du site ftp (str)
    :param liste_files: Liste des feuillets à télécharger (list)
    :param rep_output: Chemin du répertoire output. Si un/plusieurs des fichiers à télécharger s'y trouve, ces fichiers
           ne seront pas téléchargés (str)
    :return: La liste des chemin des fichiers dans la liste en entrée (list)
    '''

    # Vérification des fichiers déjà présents dans le répertoire
    print('liste des MNT adjacents: {}'.format(liste_files))
    liste_path = []
    deja_present = []
    for root, dir, files in os.walk(rep_output):
        for i in liste_files:
            for j in files:
                if i in j:
                    deja_present.append(i)
                    liste_path.append(os.path.join(root, j))

    # Liste des fichiers à télécharger, absents du répertoire output
    liste_files = [i for i in liste_files if i not in deja_present]


    if len(liste_files) > 0:
        print('liste des MNT à télécharger: {}'.format(liste_files))
        with FTP(ftpdirectory) as ftp:
            # connexion
            ftp.login()
            ftp.retrlines("LIST")
            # On se dirige vers le répertoire de base
            ftp.cwd(ftpparent)
            # Récupération de la liste des sous-répertoires
            listing = []
            ftp.retrlines("MLSD", listing.append)

            # On ordonne la liste des sous répertoires
            liste_rep_ordre = sorted([i.split(';') for i in listing], key=lambda liste: liste[-1])
            # On parcours la liste des sous-répertoires
            for rep in liste_rep_ordre:
                # On vérifie si les éléments du sous=répertoire sont des répertoire, et si le nom ou un fragment de nom
                # d'un feuillet est contenu dedans
                if rep[0].strip() == 'Type=dir' and rep[-1].strip() in [i[:3] for i in liste_files]:
                    num = rep[-1].strip()

                    print('{} dans la liste des répertoire voulus'.format(num))
                    print('Parcours du repertoire {}'.format(num))

                    # On ajoute les sous-sous-répertoires à une liste
                    ftp.cwd(rep[-1].strip())
                    liste_file = []
                    ftp.retrlines("MLSD", liste_file.append)

                    # On ordonne la liste des sous-sous répertoires
                    liste_feuillet_ordre = sorted([i.split(';') for i in liste_file], key=lambda liste: liste[-1])

                    for rep_feuillet in liste_feuillet_ordre:
                        # si le sous-sous répertoire est de type répertoire et son nom contient le numéro d'un feuillet
                        # dans la liste
                        if rep_feuillet[0].strip() == 'Type=dir' and rep_feuillet[-1].strip() in liste_files:

                            num_rep = rep_feuillet[-1].strip()

                            print('{} dans la liste des MNT voulus'.format(num_rep))
                            print('Parcours du repertoire {}'.format(num_rep))

                            # On fait une liste des fichiers à l'intérieur du répertoire
                            ftp.cwd(rep_feuillet[-1].strip())
                            liste_file = []
                            ftp.retrlines("MLSD", liste_file.append)

                            for files in liste_file:
                                info_file = files.split(';')
                                fichier_mnt = info_file[-1].strip()

                                # On vérifie si le MNT est présent dans le sous-sous répertoire
                                if fichier_mnt == 'MNT_{}.tif'.format(num_rep):

                                    print('fichier MNT: {} trouvé'.format(fichier_mnt))
                                    print('début du téléchargement')

                                    # Configuration du répertoire de sortie
                                    output_dir = os.path.join(rep_output, num_rep[:5])
                                    if not os.path.exists(output_dir):
                                        print('création du répertoire {}'.format(output_dir))
                                        os.makedirs(output_dir)

                                    # Téléchargement du fichier dans le répertoire de sortie
                                    local_filename = os.path.join(output_dir, fichier_mnt)
                                    lf = open(local_filename, "wb")
                                    ftp.retrbinary("RETR " + fichier_mnt, lf.write, 8 * 1024)
                                    lf.close()

                                    liste_path.append(local_filename)

                                    print('Fin du téléchargement')
                                    print()

                            ftp.cwd('..')
    return liste_path


def download_mnt(feuillet, path_index, col_feuillet, ftpparent, ftpdirectory, output):
    '''
    :param feuillet: numéro du feuillet sélectionné ex: '31H02NE' (str)
    :param path_index: chemin de la couche .shp de l'index des feuillets couverts par le LiDAR (forêt ouverte),
           découpage 1/20 000
    :param col_feuillet: Titre de la colonne qui comporte le numéro des feuillets dans la couche index (str)
    :param ftpparent: Répertoire de base dans lequel se trouve les fichiers à télécharger (str)
    :param ftpdirectory: adresse du site ftp (str)
    :param liste_files: Liste des feuillets à télécharger (list)
    :param rep_output: Chemin du répertoire output. Si un/plusieurs des fichiers à télécharger s'y trouve, ces fichiers
           ne seront pas téléchargés (str)
    :return: La liste des chemin des fichiers dans la liste en entrée (list)
    '''

    print('***VÉRIFICATION DES IMAGES NÉCESSAIRES ET TÉLÉCHARGEMENT***')

    # Création de la liste des MNT à télécharger
    liste = selection_mnt(feuillet, path_index, col_feuillet)

    # Téléchargement des MNT
    fichiers = download_ftp(ftpparent, ftpdirectory, liste, output)
    return fichiers


if __name__ == '__main__':

    # Lien du serveur du MFFP pour les images du feuillet
    ftpdirectory = 'transfert.mffp.gouv.qc.ca' # site ftp
    ftpparent = r'Public/Diffusion/DonneeGratuite/Foret/IMAGERIE/Produits_derives_LiDAR/' # répertoire de base

    path_index = r'C:\Users\home\Documents\Documents\APP3\Index_produit_derive_lidar\Index_produit_derive_lidar\Index_ProduitsDerive_LiDAR_Sweb.shp'
    col_feuillet = 'FCA_NO_FEU'
    feuillet = '31H02NE'

    # répertoire output
    output = r'C:\Users\home\Documents\Documents\APP2\mnt\31H02NE'

    mnts = download_mnt(feuillet=feuillet, path_index=path_index, col_feuillet=col_feuillet,
                 ftpparent=ftpparent, ftpdirectory=ftpdirectory, output=output)
