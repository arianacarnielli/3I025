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
        self.game = game
        
        self.taille = (game.spriteBuilder.rowsize, game.spriteBuilder.colsize)
        
        self.initStates = [o.get_rowcol() for o in game.layers['joueur']]
        
        self.obs_fixe = ut.recalcule_obs_fixe([w.get_rowcol() for w in game.layers['obstacle']], iterations)
        self.obs_mob = [(j, 0) for j in self.initStates]
        
        self.goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
        
        
        
    def chemin(self, iden):
        
        pos_init = (self.initStates[iden], 0)
        pos_fin = self.goalStates[iden]
        
        print(pos_init)
        print(pos_fin)
        
        #print(self.obs_fixe)
        print()
        print(self.obs_mob)
        
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
            
            voisin = ut.voisins_temp(pos, (self.obs_fixe + self.obs_mob + self.goalStates), self.taille, pos_fin)
            for pos_next in voisin:
                new_cost = cost_so_far[pos] + 1
                if pos_next not in cost_so_far or new_cost < cost_so_far[pos_next]:
                    cost_so_far[pos_next] = new_cost
                    priority = new_cost + ut.dist_man(pos_fin, pos_next[0])
                    hq.heappush(frontier,(priority, pos_next)) 
                    came_from[pos_next] = pos   
        
        chemin = []
        
        #ut.afficher_dico(came_from)
        
        try:
            while pos != pos_init:
                #print("pos",pos)
                chemin.append(pos)
                self.obs_mob.append(pos)
                (x, y), t = pos
                self.obs_mob.append(((x,y), t+1))   # eviter ecrasement tunnel
                pos = came_from[pos]
        except KeyError:
            raise ut.ThereIsNoPath
        chemin.reverse()
        return chemin
    
    
class algo_A():
    """
    """
    
    
    
    
    

        