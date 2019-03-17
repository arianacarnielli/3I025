# -*- coding: utf-8 -*-

# Nicolas, 2015-11-18

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
import pygame
import glo

import random 
import numpy as np
import sys

import heapq as hq
import operator
# ---- ---- ---- ---- ---- ----
# ---- Misc                ----
# ---- ---- ---- ---- ---- ----

"""
# on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    # on localise tous les objets ramassables
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    print ("Goal states:", goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
"""

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
    
def dist_man(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

def voisins(x, y, wallStates):
    res = []
    for i, j in [(0,1),(0,-1),(1,0),(-1,0)]:
        if ((x + i,y + j) not in wallStates) and (x + i)>=0 and (x + i)<20 and (y + j)>=0 and (y + j)<20:
            res.append((x+i, y + j))
    return res

#-------------------------------
# Building the best path with A*
#-------------------------------
  
    
def calcul_chemin(pos_init, pos_fin, wallStates):
    row,col = pos_init
    frontier =  []
    hq.heappush(frontier,(0, (row, col))) 
    came_from = {}
    cost_so_far = {}
    came_from[(row, col)] = None
    cost_so_far[(row, col)] = 0

    while len(frontier) != 0:
        _,(row,col) = hq.heappop(frontier)
        
        if (row,col) == pos_fin:
#            print ("Objet trouvé!")
#            print(came_from)
            break
        
        voisin = voisins(row, col, wallStates)
        for (row_next, col_next) in voisin:
            new_cost = cost_so_far[(row, col)] + dist_man(row, col, row_next, col_next)
            if (row_next, col_next) not in cost_so_far or new_cost < cost_so_far[(row_next, col_next)]:
                cost_so_far[(row_next, col_next)] = new_cost
                goal = pos_fin
                priority = new_cost + dist_man(goal[0], goal[1], row_next, col_next)
                hq.heappush(frontier,(priority, (row_next, col_next))) 
                came_from[(row_next, col_next)] = (row, col)   
    
    chemin = []
    x, y = pos_fin
    while not (x, y) == pos_init:
        chemin.append((x, y))
        (x, y) = came_from[(x, y)]
    chemin.reverse()
    return chemin


def liste_collisions_chemins(chemin1, chemin2):
    liste_collisions = []
    for x,y in chemin1:
        if (x,y) in chemin2:
            liste_collisions.append((x,y))
    return liste_collisions


def matrice_collisions(tab_chemins):
    n = len(tab_chemins)
    mat = [ [0]*n for i in range (n) ]
    
    for i in range(n):
        for j in range(n):
            if i==j :
                mat[i][j] = -1
                continue
            chemin1 = tab_chemins[i]
            chemin2 = tab_chemins[j]
            liste_collisions = liste_collisions_chemins(chemin1, chemin2)
            
            for x,y in liste_collisions :
                mat[i][j] = 1
    return mat

def compteur_0_collisions(matrice_collisions):
    """ dico comptabilisant le nombre de '0' pour chaque chemin
        le chemin c1 a 3 '0' => c1 ne croise pas 3 autres chemins
    """
    n = len(matrice_collisions)
    d = {i:0 for i in range(n) }
    for i in range(n):
        cpt = 0
        for j in range(n):
            if matrice_collisions[i][j]==0 : 
                cpt += 1
        d[i] = cpt
    return d

def get_argmax_key(d):
    """ retourne la clé ayant la plus grande valeur associée
    """
    return max(d.items(), key=operator.itemgetter(1))[0]

def path_doesnt_intersect(matrice_collisions, p1, lPath):
    """ intersection d'un chemin avec une liste de chemins
    """
    for path in lPath:
        if matrice_collisions[p1][path]>0:
            return False
    return True

def get_parallel_paths_to(matrice_collisions, path, dico_cpt_0_collisions):
    """ retourne une liste de chemins qui ne se croisent pas, dinstingués par
        leurs indices
    """
    lPath = [path]
    
    n = len(matrice_collisions)
    for i in range(n):
        if matrice_collisions[path][i]==0:
            if i in dico_cpt_0_collisions:
                if  path_doesnt_intersect(matrice_collisions, i, lPath):
                    lPath.append(i)
    return lPath

def indices_groupes(mc, d):
    """ retourne tous les chemins pouvant etre joués ensemble (regroupés par
        groupes), dinstingués par leurs indices
    """
    parallel_groups = []
    while (bool(d)):
        mx = get_argmax_key(d)
        parallel_group = get_parallel_paths_to(mc, mx, d)
        parallel_groups.append(parallel_group)
        for k in parallel_group:
            del d[k]
    return parallel_groups

def execution_groupes(index_groups, dico_indices, iterations=50):
    """ execution séquentielle des groupes de index_groups
        tous les chemins d'un groupe sont joués en paralèlle
    """
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
                if not (x, y) == dico_indices[path_index][1]:
                    player.set_rowcol(x,y)                
                    print ("pos :",path_index,x,y)
                else:
                    print ("Objet trouvé par le joueur ", path_index,"\n")
                    #o = player.ramasse(game.layers)
                    player.set_rowcol( dico_indices[path_index][1][0], dico_indices[path_index][1][1])
                    score[path_index]+=1
            print()
            game.mainiteration()
            if sum(score.values()) == nbPlayers:
                print ("scores:", score)
                break;
    return
    

# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer1'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():

    #for arg in sys.argv:
    iterations = 100 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations max: ", iterations)

    init()
    
    #-------------------------------
    # Initialisation
    #-------------------------------
       
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    #initStates = [(1, 3), (4, 16), (18, 1)]
    print ("Init states:", initStates)
    
    # on localise tous les objets ramassables
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    #goalStates = [(6, 7), (12, 6), (19, 8)]     # no collisions
    goalStates = [(12, 6), (19, 8), (6, 7)]     # 1 collision: 1-2
    print ("Goal states:", goalStates)
    
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    #print ("Wall states:", wallStates)
    print()
    
    
    # k : [player, goalSate, path]
    dico_indices = {i:[] for i in range(nbPlayers)}
    
    for i in range(len(players)):
        dico_indices[i].append(players[i])
    for i in range(len(players)):
        dico_indices[i].append(goalStates[i])
    
    
    tab_chemin = []
    for j in range(nbPlayers):
        tab_chemin.append(calcul_chemin(initStates[j], goalStates[j%len(goalStates)], wallStates))
        dico_indices[j].append(tab_chemin[-1])

    #afficher_dico(dico_indices)
    #affiche_monde(wallStates, tab_chemin, 20)
    
    mc = matrice_collisions(tab_chemin)
    d = compteur_0_collisions(mc)
    indice_groupes = indices_groupes(mc, d)
    #print(indice_groupes)
    execution_groupes(indice_groupes, dico_indices)

    pygame.quit()
    
    #-------------------------------
    # Placement aleatoire des fioles 
    #-------------------------------
    
    # on donne a chaque joueur une fiole a ramasser
    # en essayant de faire correspondre les couleurs pour que ce soit plus simple à suivre
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
     
# =============================================================================
#     for j in range(nbPlayers):
#         for (x, y) in tab_chemin[j]:
#             if not (x, y) ==goalStates[j]:
#                 players[j].set_rowcol(x,y)
#                 print ("pos 1:",x,y)
#                 game.mainiteration()
#             else:
#                 o = players[j].ramasse(game.layers)
#                 game.mainiteration()
#                 print ("Objet trouvé par le joueur ", j)
#                 #goalStates.remove(j) # on enlève ce goalState de la liste
#                 score[j]+=1
#                 
#     print ("scores:", score)
#     pygame.quit()
#     
# =============================================================================

    

    
    
      
    # bon ici on fait juste plusieurs random walker pour exemple...
    
# =============================================================================
#     posPlayers = initStates
# 
#     for i in range(iterations):
#         
#         for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement
#             row,col = posPlayers[j]
# 
#             x_inc,y_inc = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
#             next_row = row+x_inc
#             next_col = col+y_inc
#             # and ((next_row,next_col) not in posPlayers)
#             if ((next_row,next_col) not in wallStates) and next_row>=0 and next_row<=19 and next_col>=0 and next_col<=19:
#                 players[j].set_rowcol(next_row,next_col)
#                 print ("pos :", j, next_row,next_col)
#                 game.mainiteration()
#     
#                 col=next_col
#                 row=next_row
#                 posPlayers[j]=(row,col)
#             
#       
#         
#             
#             # si on a  trouvé un objet on le ramasse
#             if (row,col) in goalStates:
#                 o = players[j].ramasse(game.layers)
#                 game.mainiteration()
#                 print ("Objet trouvé par le joueur ", j)
#                 goalStates.remove((row,col)) # on enlève ce goalState de la liste
#                 score[j]+=1
#                 
#         
#                 # et on remet un même objet à un autre endroit
#                 x = random.randint(1,19)
#                 y = random.randint(1,19)
#                 while (x,y) in wallStates:
#                     x = random.randint(1,19)
#                     y = random.randint(1,19)
#                 o.set_rowcol(x,y)
#                 goalStates.append((x,y)) # on ajoute ce nouveau goalState
#                 game.layers['ramassable'].add(o)
#                 game.mainiteration()                
#                 
#                 break
#             
#     
#     print ("scores:", score)
#     pygame.quit()
# =============================================================================
    
    
    
    
    
    
    
if __name__ == '__main__':
    main()
    


