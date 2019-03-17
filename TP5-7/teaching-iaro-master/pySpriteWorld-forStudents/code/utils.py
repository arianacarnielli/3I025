# -*- coding: utf-8 -*-
"""
Created on Sun Mar 17 16:07:00 2019

@author: arian
"""

import heapq as hq

#==============================================================================
# Afichages
#==============================================================================
def afficher_liste(l):
    for e in l:
        print(e)
    return

def afficher_matrice(m):
    for i in range(len(m)):
        print(m[i])
    return

def afficher_dico(d):
    for k in d:
        print(k,":", d[k])
    return

def affiche_monde(wallStates, tab_chemins, taille):
    """
    Affiche un monde 2D carré de taille taille et les chemins de tab_chemin 
    (maximum 10 chemins). Les murs sont affichés comme '#', les chemins avec
    le nombre correspondant a son indice en tab_chemin.
    """
    monde = [[' ']*taille for i in range(taille)]
    chem = "0123456789"
    
    # wallsates
    for x,y in wallStates:
        monde[x][y] = '#'
    # chemins
    for i in range (len(tab_chemins)):
        for x,y in tab_chemins[i]:
            monde[x][y] = chem[i]
    
    # affichage
    for i in range(taille):
        str = ""
        for j in range(taille):
            str += monde[i][j]
        print(str)
    print()
    return

#==============================================================================
# Heuristiques pour les distances
#==============================================================================
    
def dist_man(pos1, pos2):
    """
    Calcule la distance de Manhattan entre 2 points 2D.
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

#==============================================================================
# Liste de pas possibles
#==============================================================================

def voisins(pos, obstacles, taille):
    """
    Retourne la liste de positions voisines possibles a partir de point pos et 
    le tableau des obstacles. Taille est un duplet contenant le nombre de lignes
    et de colonnes du monde.
    """
    res = []
    x, y = pos
    for i, j in [(0,1),(0,-1),(1,0),(-1,0)]:
        if ((x + i,y + j) not in obstacles) and (x + i) >= 0 and (x + i) < taille[0] and (y + j) >= 0 and (y + j) < taille[1]:
            res.append((x+i, y + j))
    return res


def detecte_collision(obstacles, chemin):
    """
    """
    for pos in chemin:
        if pos in obstacles:
            return True
    return False

#==============================================================================
# Algorithme A*
#==============================================================================
    
class ThereIsNoPath(Exception):
    pass

def calcul_chemin(pos_init, pos_fin, obstacles, taille):
    pos = pos_init
    frontier =  []
    hq.heappush(frontier,(0, pos)) 
    came_from = {}
    cost_so_far = {}
    came_from[pos] = None
    cost_so_far[pos] = 0

    while len(frontier) != 0:
        _,pos = hq.heappop(frontier)
        
        if pos == pos_fin:
#            print ("Objet trouvé!")
#            print(came_from)
            break
        
        voisin = voisins(pos, obstacles, taille)
        for pos_next in voisin:
            new_cost = cost_so_far[pos] + dist_man(pos, pos_next)
            if pos_next not in cost_so_far or new_cost < cost_so_far[pos_next]:
                cost_so_far[pos_next] = new_cost
                priority = new_cost + dist_man(pos_fin, pos_next)
                hq.heappush(frontier,(priority, pos_next)) 
                came_from[pos_next] = pos   
    
    chemin = []
    pos = pos_fin
    try:
        while pos != pos_init:
            chemin.append(pos)
            pos = came_from[pos]
    except KeyError:
        raise ThereIsNoPath
    chemin.reverse()
    return chemin


