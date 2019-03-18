# -*- coding: utf-8 -*-
"""
Created on Sun Mar 17 19:41:58 2019

@author: arian
"""

import numpy as np

import utils as ut

def ajouter_obstacles(obstacles, chemin, m):
    """
    """
    for i in range(m):
        if i >= len(chemin):
            break
        obstacles.append(chemin[i])
    
        
def modifie_slice(obstacles, pos_curr, chemin, target, m, n, max_slice, taille):
    if m < len(chemin):
        sli = chemin[:m]
        reste = chemin[m:]
    else:
        sli = chemin
        reste = []
    if ut.detecte_collision(obstacles, sli):
        print("Calcul d'un nouveau chemin de",pos_curr,"à",sli[-1],".")
        print("Obstacles:",obstacles)
        detourFound = True
        try:
            # Essaie de trouver un chemin de la position courante à sli[-1]
            detour = ut.calcul_chemin(pos_curr, sli[-1], obstacles, taille)
        except ut.ThereIsNoPath:
            detourFound = False
        if (not detourFound) or (len(detour) >= max_slice * m):
            # Si impossible ou si le detour serait trop long, calculer un chemin direct jusqu'au bout.
            try:
                return ut.calcul_chemin(pos_curr, target, obstacles,taille)
            except ut.ThereIsNoPath:
                # Si ce n'est possible, on reste arrête les m prochaines itérations
                return [pos_curr]*n + chemin
        else:
            return detour + reste
    else:
        return chemin

def execute(dico_indices, init_states, game, m = 5, n = 3, max_slice = 10, iterations = 100):
    """
    dico_indices = dictionnaire où chaque valeur correspond a un triplet [player, goalState, path]
    m = longueur qu'on regarde dans le futur pour le slicing
    n = nombre de pas de temps entre deux slicing
    """
    tours = 0
    b_max = sum([len(dico_indices[k][2]) for k in dico_indices])
    b_min = max([len(dico_indices[k][2]) for k in dico_indices])
    nbPlayers = len(dico_indices)
    
    fini = np.zeros(nbPlayers, dtype = bool)
    current_pos = init_states.copy()
    
    for i in range(iterations):
        if np.all(fini):
            break
    
        if i % n == 0:
            obstacles = [w.get_rowcol() for w in game.layers['obstacle']]
            for k in range(nbPlayers):
                obstacles.append(current_pos[k])
            
            for k in dico_indices:
                chemin = dico_indices[k][2]
                target = dico_indices[k][1]
                if fini[k]:
                    obstacles.append(target)
                    continue
                dico_indices[k][2] = modifie_slice(obstacles, current_pos[k], chemin, target, m, n, max_slice, (game.spriteBuilder.rowsize, game.spriteBuilder.colsize))
                ajouter_obstacles(obstacles, dico_indices[k][2], m)
        
        for k in dico_indices:
            if fini[k]:
                continue
            player = dico_indices[k][0]
            (x,y) = dico_indices[k][2][0]
            current_pos[k] = (x, y)
            del dico_indices[k][2][0]
            player.set_rowcol(x, y)  
            print ("pos :", k, x, y)
            
            if (x, y) == dico_indices[k][1]:
                fini[k] = True
                
        print()
        game.mainiteration()
        tours += 1
        print("tour :", tours)
            
    
    print("temps total pour la récupération de toutes les fioles : ", tours)
    print("borne superieure de temps : ", b_max)
    print("borne inferieure de temps : ", b_min)