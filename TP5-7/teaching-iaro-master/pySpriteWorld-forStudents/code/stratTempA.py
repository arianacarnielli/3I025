#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 14:19:54 2019

@author: 3407637
"""

import heapq as hq
import utils as ut

class temporal_A():
    """
    """
    
    def __init__(self, game, iterations):
        self.iterations = iterations
        self.game = game
        self.taille = (game.spriteBuilder.rowsize, game.spriteBuilder.colsize)
        
        self.initStates = [o.get_rowcol() for o in game.layers['joueur']]
        self.obs_fixe = {w.get_rowcol() for w in game.layers['obstacle']}
        self.obs_mob = {(j, 0) for j in self.initStates}
        self.goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
        
        self.tab_dist = [algo_A(self.goalStates[joueur], self.initStates[joueur], self.obs_fixe, self.taille) for joueur in range(len(self.initStates))]
        
        
    def chemin(self, iden):
        
        pos_init = (self.initStates[iden], 0)
        pos_fin = self.goalStates[iden]
        
        #print(pos_init)
        #print(pos_fin)   
        #print(self.obs_fixe)
        #print()
        #print(self.obs_mob)
        
        pos = pos_init
        frontier =  []
        hq.heappush(frontier,(0, pos)) 
        came_from = {}
        cost_so_far = {}
        came_from[pos] = None
        cost_so_far[pos] = 0
    
        while len(frontier) != 0:
            _,pos = hq.heappop(frontier)
            
            if pos[0] == pos_fin:
                #print("Objet trouvé!")
                #print(came_from)
                break
            
            voisin = ut.voisins_temp(pos, self.obs_fixe, self.obs_mob, self.taille)
            for pos_next in voisin:
                new_cost = cost_so_far[pos] + 1
                if pos_next not in cost_so_far or new_cost < cost_so_far[pos_next]:
                    cost_so_far[pos_next] = new_cost
                    priority = new_cost + self.tab_dist[iden].distance(pos_next[0])
                    #priority = new_cost + ut.dist_man(pos_fin, pos_next[0])
                    hq.heappush(frontier,(priority, pos_next)) 
                    came_from[pos_next] = pos   
        
        chemin = []
        
        #ut.afficher_dico(came_from)
        
        try:
            while pos != pos_init:
                #print("pos",pos)
                chemin.append(pos)
                self.obs_mob.add(pos)
                (x, y), t = pos
                self.obs_mob.add(((x,y), t+1))   # eviter ecrasement tunnel
                pos = came_from[pos]
        except KeyError:
            raise ut.ThereIsNoPath
        
        for t in range(chemin[0][1] + 2, self.iterations):
            self.obs_mob.add((chemin[0][0], t))
            
        chemin.reverse()
        return chemin
    
    
class algo_A():
    """
    """
    def __init__(self, pos_init, pos_fin, obs_fixe, taille):
        """
        pos_init = position de la fiole cible (on fait le chemin inverse)
        pos_fin = position initiale du joueur.
        """
        self.pos_init = pos_init
        self.pos_fin = pos_fin
        self.obs_fixe = obs_fixe
        self.taille =taille
        
        self.frontier =  []
        hq.heappush(self.frontier,(0, self.pos_init)) 

        self.cost_so_far = {}
        self.cost_so_far[self.pos_init] = 0
        
        self.ferme = set()
    
    
    def distance(self, cible):    
        while cible not in self.ferme:
            _,pos = hq.heappop(self.frontier)
            self.ferme.add(pos) 
            
            voisin = ut.voisins(pos, self.obs_fixe, self.taille, self.pos_fin)
            for pos_next in voisin:
                new_cost = self.cost_so_far[pos] + 1
                if pos_next not in self.cost_so_far or new_cost < self.cost_so_far[pos_next]:
                    self.cost_so_far[pos_next] = new_cost
                    priority = new_cost + ut.dist_man(self.pos_fin, pos_next)
                    hq.heappush(self.frontier,(priority, pos_next)) 

        return self.cost_so_far[cible]

    

        