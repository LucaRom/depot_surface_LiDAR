'''
David Ethier, Yves Voirin,  2020
'''

import os
from ftplib import FTP
import geopandas as gpd


def selection_mnt(feuillet, path_index, col_feuillet):

    index = gpd.read_file(path_index)
    geom_feuillet = index['geometry'][index[col_feuillet] == feuillet].values[0]
    index['intersect'] = index.intersects(geom_feuillet)
    liste_download = (list(index[col_feuillet][index['intersect'] == True].values))
    return liste_download


def download_ftp(ftpparent, ftpdirectory, liste_files, rep_output):

    for i in liste_files:
        if os.path.exists(os.path.join(rep_output, 'MNT_{}.tif'.format(i))):
            liste_files.remove(i)
    print(liste_files)

    with FTP(ftpdirectory) as ftp:
        ftp.login()
        ftp.retrlines("LIST")
        ftp.cwd(ftpparent)
        listing = []
        ftp.retrlines("MLSD", listing.append)

        liste_rep_ordre = sorted([i.split(';') for i in listing], key=lambda liste: liste[-1])

        for rep in liste_rep_ordre:

            if rep[0].strip() == 'Type=dir' and rep[-1].strip() in [i[:3] for i in liste_files]:
                num = rep[-1].strip()

                print('{} dans la liste des répertoire voulus'.format(num))
                print('Parcours du repertoire {}'.format(num))

                ftp.cwd(rep[-1].strip())
                liste_file = []
                ftp.retrlines("MLSD", liste_file.append)

                liste_feuillet_ordre = sorted([i.split(';') for i in liste_file], key=lambda liste: liste[-1])

                for rep_feuillet in liste_feuillet_ordre:

                    if rep_feuillet[0].strip() == 'Type=dir' and rep_feuillet[-1].strip() in liste_files:

                        num_rep = rep_feuillet[-1].strip()

                        print('{} dans la liste des MNT voulus'.format(num_rep))
                        print('Parcours du repertoire {}'.format(num_rep))

                        ftp.cwd(rep_feuillet[-1].strip())
                        liste_file = []
                        ftp.retrlines("MLSD", liste_file.append)

                        for files in liste_file:
                            info_file = files.split(';')
                            fichier_mnt = info_file[-1].strip()

                            if fichier_mnt == 'MNT_{}.tif'.format(num_rep):

                                print('fichier MNT: {} trouvé'.format(fichier_mnt))
                                print('début du téléchargement')

                                #output_dir = os.path.join(rep_output, num_rep[:5])
                                if not os.path.exists(rep_output):
                                    print('création du répertoire {}'.format(rep_output))
                                    os.makedirs(output)

                                local_filename = os.path.join(rep_output, fichier_mnt)
                                lf = open(local_filename, "wb")
                                ftp.retrbinary("RETR " + fichier_mnt, lf.write, 8 * 1024)
                                lf.close()

                                print('Fin du téléchargement')
                                print()

                        ftp.cwd('..')


def download_mnt(feuillet, path_index, col_feuillet, ftpparent, ftpdirectory, output):

    # Création de la liste des MNT à télécharger
    liste = selection_mnt(feuillet, path_index, col_feuillet)

    # Téléchargement des MNT
    download_ftp(ftpparent, ftpdirectory, liste, output)


if __name__ == '__main__':

    # Lien du serveur du MFFP pour les images du feuillet
    ftpdirectory = 'transfert.mffp.gouv.qc.ca' # site ftp
    ftpparent = r'Public/Diffusion/DonneeGratuite/Foret/IMAGERIE/Produits_derives_LiDAR/' # répertoire de base

    path_index = r'C:\Users\home\Documents\Documents\APP3\Index_produit_derive_lidar\Index_produit_derive_lidar\Index_ProduitsDerive_LiDAR_Sweb.shp'
    col_feuillet = 'FCA_NO_FEU'
    feuillet = '31H02NE'

    # répertoire output
    output = r'C:\Users\home\Documents\Documents\APP2\mnt\31H02NE'

    download_mnt(feuillet=feuillet, path_index=path_index, col_feuillet=col_feuillet,
                 ftpparent=ftpparent, ftpdirectory=ftpdirectory, output=output)
