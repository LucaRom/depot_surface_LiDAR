'''
David Ethier, Yves Voirin,  2020
'''

import os
from ftplib import FTP


# intrants
feuillet = '31H'
feuillet_debut = '31H01'
feuillet_fin = '31H02'

# répertoire output
output = r'D:\DATA\MNT'

# Lien du serveur du MFFP pour les images du feuillet
ftpdirectory = 'transfert.mffp.gouv.qc.ca' # site ftp
parent = r'Public/Diffusion/DonneeGratuite/Foret/IMAGERIE/Produits_derives_LiDAR/' # répertoire de base


parent = os.path.join(parent, feuillet)


def liste_mnt_a_download(feuillet, div_debut, div_fin):

    liste_voulu = []
    if feuillet[:3] == div_debut[:3] and feuillet[:3] == div_fin[:3]:

        nb_deb = int(div_debut[3:5])
        nb_fin = int(div_fin[3:5])
        nb_fois = nb_fin - nb_deb + 1

        compte_feuillet = nb_deb
        for i in range(nb_fois):
            liste_div = ['NE','NO','SE','SO']
            for j in liste_div:
                compte = None
                if compte_feuillet < 10:
                    compte = '0'+ str(compte_feuillet)
                else:
                    compte = str(compte_feuillet)

                a = '{}{}{}'.format(feuillet, compte, j)
                liste_voulu.append(a)
            compte_feuillet += 1

        return liste_voulu


liste_voulu = liste_mnt_a_download(feuillet, feuillet_debut, feuillet_fin)
print('liste des MNT voulues: {}'.format(liste_voulu))
print()


with FTP(ftpdirectory) as ftp:
    ftp.login()
    ftp.retrlines("LIST")
    ftp.cwd(parent)
    listing = []
    ftp.retrlines("MLSD", listing.append)

    liste_feuillet_ordre = sorted([i.split(';') for i in listing], key=lambda liste: liste[-1])

    for rep_feuillet in liste_feuillet_ordre:

        if rep_feuillet[0].strip() == 'Type=dir' and rep_feuillet[-1].strip() in liste_voulu :
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

                    output_dir = os.path.join(output, num_rep[:5])
                    if not os.path.exists(output_dir):
                        print('création du répertoire {}'.format(output_dir))
                        os.mkdir(output_dir)

                    local_filename = os.path.join(output_dir, fichier_mnt)
                    lf = open(local_filename, "wb")
                    ftp.retrbinary("RETR " + fichier_mnt, lf.write, 8 * 1024)
                    lf.close()

                    print('Fin du téléchargement')
                    print()

            ftp.cwd('..')



# wbt = whitebox.WhiteboxTools()
# RUST_BACKTRACE=1
# path = r'D:\DATA\raster'
# wbt.set_working_dir(path)
# wbt.verbose = False
# output = os.path.join(path, 'tpi_wb_python.tif')
# wbt.relative_topographic_position('MNT_31H02NE_5X5.tif', output, 200, 200)
