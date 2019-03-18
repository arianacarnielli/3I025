# -*- coding: utf-8 -*-
"""
Created on Sun Mar 17 18:22:12 2019

@author: arian
"""
#==============================================================================
# Import des bibliothèques
#==============================================================================
import pygame
import sys

#==============================================================================
# Import des fonctions codées
#==============================================================================
import stratCoopBase as scb
import stratSlicing as ss
import utils as ut

#==============================================================================
# Import de code fourni par le prof
#==============================================================================
sys.path.append('../')
from gameclass import Game
from spritebuilder import SpriteBuilder
from ontology import Ontology

#==============================================================================
# Main
#==============================================================================

game = Game()

def init(_boardname = None):
    global player,game
    name = _boardname if _boardname is not None else 'pathfindingWorld_MultiPlayer8'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 1.5  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    
def mainCoopBase():

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
    print ("Init states:", initStates)
    
    # on localise tous les objets ramassables
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]

    # Pour garantir qu'on aura une collision a la carte par defaut
    #goalStates = [(12, 6), (19, 8), (6, 7)]     # 1 collision: 1-2
    print ("Goal states:", goalStates)
    
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    #print ("Wall states:", wallStates)
    print()
    
    
    # k : [player, goalState, path]
    dico_indices = {i:[] for i in range(nbPlayers)}
    
    for i in range(len(players)):
        dico_indices[i].append(players[i])
    for i in range(len(players)):
        dico_indices[i].append(goalStates[i])
    
    
    tab_chemin = []
    for j in range(nbPlayers):
        tab_chemin.append(ut.calcul_chemin(initStates[j], goalStates[j%len(goalStates)], wallStates, (game.spriteBuilder.rowsize, game.spriteBuilder.colsize)))           
        dico_indices[j].append(tab_chemin[-1])

    #afficher_dico(dico_indices)
    #affiche_monde(wallStates, tab_chemin, 20)
    
    mc = scb.matrice_collisions(tab_chemin)
    d = scb.compteur_0_collisions(mc)
    indice_groupes = scb.indices_groupes(mc, d)
    #print(indice_groupes)
    scb.execution_groupes(indice_groupes, dico_indices, game)

    pygame.quit()
    
def mainSlicing():
    iterations = 100 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations max: ", iterations)

    init()
    
    #-------------------------------
    # Initialisation
    #-------------------------------
    
    boardSize = (game.spriteBuilder.rowsize, game.spriteBuilder.colsize)
    
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
       
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    # on localise tous les objets ramassables
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    #goalStates.reverse()
    # Pour garantir qu'on aura une collision a la carte par defaut
    #goalStates = [(12, 6), (19, 8), (6, 7)]     # 1 collision: 1-2
    
    print ("Goal states:", goalStates)
    
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    #print ("Wall states:", wallStates)
    print()
    
    # k : [player, goalState, path]
    dico_indices = {i:[] for i in range(nbPlayers)}
    
    for i in range(nbPlayers):
        dico_indices[i].append(players[i])
        dico_indices[i].append(goalStates[i])
        dico_indices[i].append(ut.calcul_chemin(initStates[i], goalStates[i%len(goalStates)], wallStates, boardSize))
    
    ut.affiche_monde(wallStates, [dico_indices[k][2] for k in dico_indices], 20)    
    ss.execute(dico_indices, initStates, game, iterations = iterations)

    pygame.quit()
    
if __name__ == '__main__':
    #mainCoopBase()
    mainSlicing()
    
