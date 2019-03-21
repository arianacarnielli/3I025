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
        
    def setGoalStates(self, goalStates):
        self.goalStates = goalStates
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
        
        for t in range(chemin[0][1] + 1, self.iterations):
            if (chemin[0][0], t) in self.obs_mob:
                raise ut.ThereIsNoPath("Sorry :'( J'arrive à la fiole mais je ne peux pas y rester car quelqu'un d'autre veut passer ici après !")
            self.obs_mob.add((chemin[0][0], t))
            
        chemin.reverse()
        return chemin
    
    
class temporal_A_D():
    """
    """
    
    def __init__(self, game, iterations, d):
        self.iterations = iterations
        self.game = game
        self.taille = (game.spriteBuilder.rowsize, game.spriteBuilder.colsize)
        self.players = [o for o in game.layers['joueur']] 
        self.initStates = [p.get_rowcol() for p in self.players]
        self.nbPlayers = len(self.players)
        
        self.obs_fixe = {w.get_rowcol() for w in game.layers['obstacle']}
        self.obs_mob = {(self.initStates[p], t):p for p in range(self.nbPlayers) for t in [0, 1]}
        self.goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
        
        self.tab_dist = [algo_A(self.goalStates[joueur], self.initStates[joueur], self.obs_fixe, self.taille) for joueur in range(self.nbPlayers)]
        self.d = d
        
    def setGoalStates(self, goalStates):
        self.goalStates = goalStates
        self.tab_dist = [algo_A(self.goalStates[joueur], self.initStates[joueur], self.obs_fixe, self.taille) for joueur in range(self.nbPlayers)]
        

    def execute(self):        
        tab_joueur = [self.chemin(k, 0, self.d + 2*k) for k in range(self.nbPlayers)]
        
        for it in range(self.iterations):
            if self.is_finished():
                break
            for j in range(self.nbPlayers):
                if tab_joueur[j] == []:
                    self.initStates[j] = self.players[j].get_rowcol()
                    tab_joueur[j] = self.chemin(j, it, self.d)
                    # Si je n'ai toujours pas trouvé un chemin (ça peut arriver!!)
                    if tab_joueur[j] == []:
                        print("Joueur",j,"bloqué")
                        # On oublie les chemins de tout le monde et on recommence !
                        self.obs_mob = {(self.players[p].get_rowcol(), it + dt):p for p in range(self.nbPlayers) for dt in [0, 1]}
                        tab_joueur = [[] for k in range(self.nbPlayers)]
                        # On recalcule à partir du joueur courant
                        for k in range(j, j + self.nbPlayers):
                            kk = k % self.nbPlayers
                            self.initStates[kk] = self.players[kk].get_rowcol()
                            tab_joueur[kk] = self.chemin(kk, it, self.d + kk)
                        # Si on est vraiment vraiment vraiment bloqué
                        if tab_joueur[j] == []:
                            raise ut.ThereIsNoPath("Wow, I'm completely stuck! Where am I??")
            for j in range(self.nbPlayers):
                pos,_ = tab_joueur[j].pop(0)
                self.players[j].set_rowcol(pos[0], pos[1])                
                print ("pos :",j,pos[0], pos[1])
            print()
            self.game.mainiteration()
            print("tour :", it)
        
    def is_finished(self):
        for i in range(self.nbPlayers):
            if self.players[i].get_rowcol() != self.goalStates[i]:
                return False
        return True
        
    def chemin(self, iden, t0, d):
        pos_init = (self.initStates[iden], t0)
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
            
            if pos[1] == t0 + d:
                #print(came_from)
                break
            
            voisin = ut.voisins_tempD(iden, pos, self.obs_fixe, self.obs_mob, self.taille)
            for pos_next in voisin:
                new_cost = cost_so_far[pos] + cost(pos, pos_next, pos_fin)
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
                self.obs_mob[pos] = iden
                (x, y), t = pos
                self.obs_mob[((x,y), t+1)] = iden   # eviter ecrasement tunnel
                pos = came_from[pos]
        except KeyError:
            raise ut.ThereIsNoPath
            
        chemin.reverse()
        
        return chemin
    
def cost(pos, pos_next, pos_fin):
    if pos[0] == pos_next[0] and pos_next[0] == pos_fin:
        return 0
    return 1


    
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
        
        if self.pos_init==(6, 7):
            print(self.taille)
            print(self.obs_fixe)
    
    
    def distance(self, cible):
#        print("Calcul de distance")
#        print("Je suis la fiole de la position",self.pos_init)
#        print("Le joueur à la position",self.pos_fin,"veut venir me chercher")
#        print("Je veux calculer le chemin le plus court à",cible)
        while cible not in self.ferme:
            #print(self.frontier)
            _,pos = hq.heappop(self.frontier)
            self.ferme.add(pos)
            #if self.pos_init==(6, 7) and pos==(18, 0):
            if pos==(18, 0):
                print("Je viens de rajouter (18, 0)")
            
            voisin = ut.voisins(pos, self.obs_fixe, self.taille, self.pos_fin)
            #if self.pos_init==(6, 7) and pos==(18, 0):
            if pos==(18, 0):
                print("Mes voisins sont",voisin)
            for pos_next in voisin:
                new_cost = self.cost_so_far[pos] + 1
                if pos_next not in self.cost_so_far or new_cost < self.cost_so_far[pos_next]:
                    self.cost_so_far[pos_next] = new_cost
                    priority = new_cost + ut.dist_man(self.pos_fin, pos_next)
                    hq.heappush(self.frontier,(priority, pos_next)) 

        return self.cost_so_far[cible]

    

        