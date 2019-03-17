# -*- coding: utf-8 -*-
"""
Created on Sun Mar 17 16:26:48 2019

@author: arian
"""

import operator
import numpy as np

def liste_collisions_chemins(chemin1, chemin2):
    """
    retourne une liste avec toutes les positions en commun entre chemin1 et chemin2
    """
    liste_collisions = []
    for pos in chemin1:
        if pos in chemin2:
            liste_collisions.append(pos)
    return liste_collisions


def matrice_collisions(tab_chemins):
    """
    Cree une matrice n x n, ou n est la quantité de chemins en tab_chemins.
    La case i x j de la matrice contient 1, s'il y a de collisions entre les 
    chemins i et j, 0 sinon et -1 si i = j. 
    """
    n = len(tab_chemins)
    mat = np.eye(n, dtype = int) * -1   
    for i in range(n):
        for j in range(i + 1, n):
            chemin1 = tab_chemins[i]
            chemin2 = tab_chemins[j]
            liste_collisions = liste_collisions_chemins(chemin1, chemin2)
            if liste_collisions != []: 
                mat[i,j] = 1
                mat[j,i] = 1
    return mat

def compteur_0_collisions(matrice_collisions):
    """
    dictionnaire comptabilisant le nombre de '0' pour chaque chemin
    le chemin c1 a 3 '0' => c1 ne croise pas 3 autres chemins
    """
    n = matrice_collisions.shape[0]
    dico = {i:0 for i in range(n)}
    for i in range(n):
        dico[i] = (matrice_collisions[i,:] == 0).sum()
    return dico

def get_argmax_key(dico):
    """ 
    retourne la clé ayant la plus grande valeur associée
    """
    return max(dico.items(), key = operator.itemgetter(1))[0]

def path_doesnt_intersect(matrice_collisions, p1, lPath):
    """ 
    intersection d'un chemin avec une liste de chemins
    """
    for path in lPath:
        if matrice_collisions[p1, path] > 0:
            return False
    return True

def get_parallel_paths_to(matrice_collisions, path, dico_cpt_0_collisions):
    """ 
    retourne une liste de chemins qui ne se croisent pas, dinstingués par
    leurs indices
    """
    lPath = [path]
    n = matrice_collisions.shape[0]
    for i in range(n):
        if matrice_collisions[path, i] == 0:
            if i in dico_cpt_0_collisions:
                if  path_doesnt_intersect(matrice_collisions, i, lPath):
                    lPath.append(i)
    return lPath

def indices_groupes(matrice_collisions, dico):
    """ 
    retourne tous les chemins pouvant etre joués ensemble (regroupés par
    groupes), dinstingués par leurs indices
    """
    parallel_groups = []
    while (bool(dico)):
        mx = get_argmax_key(dico)
        parallel_group = get_parallel_paths_to(matrice_collisions, mx, dico)
        parallel_groups.append(parallel_group)
        for k in parallel_group:
            del dico[k]
    return parallel_groups

def execution_groupes(index_groups, dico_indices, game, iterations = 50):
    """ 
    execution séquentielle des groupes de index_groups
    tous les chemins d'un groupe sont joués en paralèlle
    """
    tours = 0
    b_max = sum([len(dico_indices[k][2]) for k in dico_indices])
    b_min = max([len(dico_indices[k][2]) for k in dico_indices])
    for index_group in index_groups:
        nbPlayers = len(index_group)
        score = {k:0 for k in index_group}
        for i in range(iterations):
            for path_index in index_group:
                player = dico_indices[path_index][0]
                if len(dico_indices[path_index][2]) == 0 :
                    continue
                (x,y) = dico_indices[path_index][2][0]
                del dico_indices[path_index][2][0]
                if (x, y) != dico_indices[path_index][1]:
                    player.set_rowcol(x,y)                
                    print ("pos :",path_index,x,y)
                else:
                    print ("Objet trouvé par le joueur ", path_index,"\n")
                    #o = player.ramasse(game.layers)
                    player.set_rowcol( dico_indices[path_index][1][0], dico_indices[path_index][1][1])
                    score[path_index]+=1
            print()
            game.mainiteration()
            tours += 1
            if sum(score.values()) == nbPlayers:
                print ("scores:", score)
                break
    print("temps total pour la récupération de toutes les fioles : ", tours)
    print("borne superieure de temps : ", b_max)
    print("borne inferieure de temps : ", b_min)
