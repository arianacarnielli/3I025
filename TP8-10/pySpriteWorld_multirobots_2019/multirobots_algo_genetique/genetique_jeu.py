# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 18:18:27 2019

@author: arian
"""

import numpy as np

from random import shuffle
from robosim import Game, throw_rays_for_many_players, efface, Turtle, init, pygame
from genetique_agent import AgentTypeA, AgentTypeB

#==============================================================================
# IMMPORTANT ! pas d'affichage graphique grace aux deux lignes suivantes! 
#==============================================================================
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

game = Game()

class Jeu():
    maxSensorDistance = 30 # utilisé localement.
    maxRotationSpeed = 5
    maxTranslationSpeed = 1
    SensorBelt = [-170,-80,-40,-20,+20,40,80,+170] # angles en degres des senseurs

    screen_width = 512 #512,768,... -- multiples de 32  
    screen_height = 512 #512,768,... -- multiples de 32
    frameskip = 4000 # 0: no-skip. >1: skip n-1 frames
    verbose = False # permet d'afficher le suivi des agents (informations dans la console)
    showSensors = False

    agents = []
    
    def __init__(self, maxIterations, nbAgents, game):
        self.maxIterations = maxIterations
        self.nbAgents = nbAgents
        self.game = game
        init('empty', MyTurtle, self.screen_width, self.screen_height) # display is re-dimensioned, turtle acts as a template to create new players/robots
        self.game.auto_refresh = False # display will be updated only if game.mainiteration() is called
        self.game.frameskip = self.frameskip
        
    def reset(self, arena, w):
        self.arena = arena
        self.iteration = 0
        self.startoccupancyGrid()
        self.game.del_all_sprites('obstacle')
        self.game.del_all_sprites('joueur')
        AgentTypeA.agentIdCounter = 0
        AgentTypeB.agentIdCounter = 0
        self.setupArena()
        self.setupAgents(w)
        self.game.mainiteration()

    def run(self):
        for It in range(self.maxIterations):
            self.stepWorld()
            self.game.mainiteration()

    def startoccupancyGrid(self):    
        self.occupancyGrid = np.array([["_" for x in range(self.screen_width//16)] for y in range(self.screen_height//16)], dtype = str)
    
    def setupAgents(self, w):
        # Make agents
        self.agents = []
        nbAgentsTypeA = nbAgentsTypeB = self.nbAgents // 2
        nbAgentsCreated = 0
    
        for i in range(nbAgentsTypeA):
            position = (16 , 200+32*i)
            orientation = 0
            p = self.game.add_players(position, None, tiled=False)
            p.oriente(orientation)
            p.numero = nbAgentsCreated
            nbAgentsCreated += 1
            if i % 2 == 0:
                self.agents.append(AgentTypeA(p, self, w[0:22]))
            else:
                self.agents.append(AgentTypeA(p, self, w[22:44]))
    
        for i in range(nbAgentsTypeB):
            position = (486 , 200+32*i)
            orientation = 180
            p = self.game.add_players(position, None, tiled=False)
            p.oriente(orientation)
            p.numero = nbAgentsCreated
            nbAgentsCreated += 1
            self.agents.append(AgentTypeB(p, self))
    
    def setupArena(self):
        if self.arena == 0:
            for i in range(6,13):
                self.addObstacle(row=3,col=i)
            for i in range(3,10):
                self.addObstacle(row=12,col=i)
            self.addObstacle(row=4,col=12)
            self.addObstacle(row=5,col=12)
            self.addObstacle(row=6,col=12)
            self.addObstacle(row=11,col=3)
            self.addObstacle(row=10,col=3)
            self.addObstacle(row=9,col=3)
        elif self.arena == 1:
            return
        elif self.arena == 2:
            for i in range(0,8):
                self.addObstacle(row=i,col=7)
            for i in range(8,16):
                self.addObstacle(row=i,col=8)
        else:
            w = self.screen_width//32
            h = self.screen_height//32
            for i in range(h):
                if i==h//4:
                    continue
                self.addObstacle(row=i,col=w//2)
                self.addObstacle(row=i,col=w//2-1)
        
    def addObstacle(self, row, col):
        # le sprite situe colone 13, ligne 0 sur le spritesheet
        self.game.add_new_sprite('obstacle',tileid=(0,13),xy=(col,row),tiled=True)
            
            
    def updateSensors(self):
        # throw_rays...(...) : appel couteux (une fois par itération du simulateur). permet de mettre à jour le masque de collision pour tous les robots.
        self.sensors = throw_rays_for_many_players(self.game, self.game.layers['joueur'], self.SensorBelt, max_radius = self.maxSensorDistance +self.game.player.diametre_robot() , show_rays = self.showSensors)
    
    def stepWorld(self):
        efface()
        self.updateSensors()
        # chaque agent se met à jour. L'ordre de mise à jour change à chaque fois (permet d'éviter des effets d'ordre).
        shuffledIndexes = [i for i in range(len(self.agents))]
        shuffle(shuffledIndexes)
        for i in range(len(self.agents)):
            self.agents[shuffledIndexes[i]].step()
            # met à jour la grille d'occupation
            coord = self.agents[shuffledIndexes[i]].getRobot().get_centroid()
            self.occupancyGrid[int(coord[0])//16, int(coord[1])//16] = self.agents[shuffledIndexes[i]].getType() # first come, first served
    
    def computeOccupancyGrid(self):
        nbA = (self.occupancyGrid == "A").sum()
        nbB = (self.occupancyGrid == "B").sum()
        return nbA, nbB, (self.occupancyGrid.size - nbA - nbB)

class MyTurtle(Turtle): # also: limit robot speed through this derived class
    def rotate(self,a):
        mx = Jeu.maxRotationSpeed
        Turtle.rotate(self, max(-mx,min(a,mx)))

if __name__=="__main__":
    jeu = Jeu(maxIterations = 4000, nbAgents = 8, game = game)
    for i in range(4):
        jeu.reset(i%4)
        jeu.run()
        print(jeu.computeOccupancyGrid())
    pygame.quit()