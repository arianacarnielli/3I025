#!/usr/bin/env python
# -*- coding: utf-8 -*-

from robosim import Game, color, circle, throw_rays_for_many_players, efface, Turtle, init, pygame
from random import random, shuffle
import sys
import atexit
import numpy as np

#==============================================================================
# IMMPORTANT ! pas d'affichage graphique grace aux deux lignes suivantes! 
#==============================================================================
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  variables globales   '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

game = Game()
agents = []

arena = 0

nbAgents = 8 # doit être pair et inférieur a 32
maxSensorDistance = 30              # utilisé localement.
maxRotationSpeed = 5
maxTranslationSpeed = 1
SensorBelt = [-170,-80,-40,-20,+20,40,80,+170]  # angles en degres des senseurs

screen_width=512 #512,768,... -- multiples de 32  
screen_height=512 #512,768,... -- multiples de 32

maxIterations = 2000 # infinite: -1
showSensors = False
frameskip = 4   # 0: no-skip. >1: skip n-1 frames
verbose = False # permet d'afficher le suivi des agents (informations dans la console)

occupancyGrid = []
for y in range(screen_height//16):
    l = []
    for x in range(screen_width//16):
        l.append("_")
    occupancyGrid.append(l)

iteration = 0

'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Agent générique      '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

class Agent(object):
    agentIdCounter = 0 # use as static
    id = -1
    robot = -1
    agentType = "X"
    etat = 0
    
    translationValue = 0 # ne pas modifier directement
    rotationValue = 0 # ne pas modifier directement

    def __init__(self,robot):
        self.robot = robot
        self.robot.teamname = self.teamname

    def getType(self):
        return self.agentType

    def getRobot(self):
        return self.robot

    teamname = "Agent"

    def stepController(self):
        pass

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def step(self):
        self.stepController()
        self.move()

    def move(self):
        self.robot.forward(self.translationValue)
        self.robot.rotate(self.rotationValue)

    def getDistanceAtSensor(self,id):
        sensor_infos = sensors[self.robot] # sensor_infos est une liste de namedtuple (un par capteur).
        return min(sensor_infos[id].dist_from_border,maxSensorDistance) / maxSensorDistance

    def getObjectTypeAtSensor(self,id):
        if sensors[self.robot][id].dist_from_border > maxSensorDistance:
            return 0 # nothing
        elif sensors[self.robot][id].layer == 'joueur':
            return 2 # robot
        else:
            return 1 # wall/border

    def getRobotInfoAtSensor(self,id):
        if sensors[self.robot][id].dist_from_border < maxSensorDistance and sensors[self.robot][id].layer == 'joueur':
            otherRobot = sensors[self.robot][id].sprite
            info = {'id': otherRobot.numero, 'centroid': otherRobot.get_centroid(), 'orientation': otherRobot.orientation(), 'teamname': otherRobot.teamname }
            return info
        else:
            #print ("[WARNING] getPlayerInfoAtSensor(.): not a robot!")
            return None

    def setTranslationValue(self,value):
        if value > 1:
            #♠print ("[WARNING] translation value not in [-1,+1]. Normalizing.")
            value = maxTranslationSpeed
        elif value < -1:
            #print ("[WARNING] translation value not in [-1,+1]. Normalizing.")
            value = -maxTranslationSpeed
        else:
            value = value * maxTranslationSpeed
        self.translationValue = value

    def setRotationValue(self,value):
        if value > 1:
            #print ("[WARNING] translation value not in [-1,+1]. Normalizing.")
            value = maxRotationSpeed
        elif value < -1:
            #print ("[WARNING] translation value not in [-1,+1]. Normalizing.")
            value = -maxRotationSpeed
        else:
            value = value * maxRotationSpeed
        self.rotationValue = value

'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Agent "A"            '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
class AgentTypeA(Agent):
    agentType = "A"

    def __init__(self, robot, w):
        self.w = w
        super().__init__(robot)
        self.id = AgentTypeA.agentIdCounter
        AgentTypeA.agentIdCounter = AgentTypeA.agentIdCounter + 1
        #print ("robot #", self.id, " -- init")

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-= JOUEUR A -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= 
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-= pour l'évaluation, seul le teamname et la fct  stepController(.)  =-=
    # =-=-=-=-= seront utilisés. Assurez-vous donc que tout votre code utile est  =-=
    # =-=-=-=-= auto-contenu dans la fonction stepControlelr. Vous pouvez changer =-=
    # =-=-=-=-= teamname (c'est même conseillé si vous souhaitez que vos robots   =-=
    # =-=-=-=-= se reconnaissent entre eux.                                       =-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    teamname = "AAAH" # A modifier avec le nom de votre équipe

    def stepController(self):    
        # cette méthode illustre l'ensemble des fonctions et informations que vous avez le droit d'utiliser.
        # tout votre code doit tenir dans cette méthode. La seule mémoire autorisée est la variable self.etat
        # (c'est un entier).

        color( (0,255,0) )
        circle( *self.getRobot().get_centroid() , r = 22) # je dessine un rond vert autour de ce robot


        # =============================================================================
        # Strategie
        # =============================================================================
        middleId = nbAgents // 2 - 0.5
        ar_dist = np.array([self.getDistanceAtSensor(i) for i in range(len(SensorBelt))])
        ar_dist = 1 - ar_dist
        ar_type = np.array([self.getObjectTypeAtSensor(i) for i in range(len(SensorBelt))])
        ar_info = np.array([self.getRobotInfoAtSensor(i)["id"] if ar_type[i]==2 else middleId for i in range(ar_type.size)])
        ar_info = np.sign((ar_info - middleId)*(self.robot.numero - middleId))
        
        sensors = np.empty(2*ar_dist.size + 1)
        sensors[0] = 1
        sensors[1:(ar_dist.size+1)] = ar_dist * (ar_type % 2)
        sensors[(ar_dist.size+1):] = ar_dist * ar_info        
        
        self.setRotationValue(min(1, max(-1, self.w.dot(sensors) + 0.2*random() - 0.1)))
        self.setTranslationValue(1)
        
        # monitoring (optionnel - changer la valeur de verbose)
        if verbose == True:
            print ("Robot #"+str(self.id)+" [teamname:\""+str(self.teamname)+"\"] [variable mémoire = "+str(self.etat)+"] :")
            for i in range(len(SensorBelt)):
                print ("\tSenseur #"+str(i)+" (angle: "+ str(SensorBelt[i])+"°)")
                print ("\t\tDistance  :",self.getDistanceAtSensor(i))
                print ("\t\tType      :",self.getObjectTypeAtSensor(i)) # 0: rien, 1: mur ou bord, 2: robot
                print ("\t\tRobot info:",self.getRobotInfoAtSensor(i)) # dict("id","centroid(x,y)","orientation") (si pas de robot: renvoi "None" et affiche un avertissement dans la console

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Agent "B"            '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

class AgentTypeB(Agent):
    agentType = "B"

    def __init__(self, robot):
        super().__init__(robot)
        self.id = AgentTypeB.agentIdCounter
        AgentTypeB.agentIdCounter = AgentTypeB.agentIdCounter + 1
        #print ("robot #", self.id, " -- init")
        
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-= JOUEUR B -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    teamname = "Equipe Test" # A modifier avec le nom de votre équipe

    def stepController(self):

        color( (255,0,0) )
        circle( *self.getRobot().get_centroid() , r = 22) # je dessine un rond bleu autour de ce robot

        distGauche = self.getDistanceAtSensor(2) # renvoi une valeur normalisée entre 0 et 1
        distDroite = self.getDistanceAtSensor(5) # renvoi une valeur normalisée entre 0 et 1
        
        if distGauche < distDroite:
            self.setRotationValue( +1 )
        elif distGauche > distDroite:
            self.setRotationValue( -1 )
        else:
            self.setRotationValue( 0 )

        self.setTranslationValue(1) # normalisé -1,+1
        
        # monitoring (optionnel - changer la valeur de verbose)
        if verbose == True:
            print ("Robot #"+str(self.id)+" [teamname:\""+str(self.teamname)+"\"] [variable mémoire = "+str(self.etat)+"] :")
            for i in range(8):
                print ("\tSenseur #"+str(i)+" (angle: "+ str(SensorBelt[i])+"°)")
                print ("\t\tDistance  :",self.getDistanceAtSensor(i))
                print ("\t\tType      :",self.getObjectTypeAtSensor(i)) # 0: nothing, 1: wall/border, 2: robot
                print ("\t\tRobot info:",self.getRobotInfoAtSensor(i)) # dict("id","centroid(x,y)","orientation") (if not a robot: returns None and display a warning)

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Fonctions init/step  '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

def setupAgents(w):
    global screen_width, screen_height, nbAgents, agents, game

    # Make agents

    nbAgentsTypeA = nbAgentsTypeB = nbAgents // 2
    nbAgentsCreated = 0

    for i in range(nbAgentsTypeA):
        p = game.add_players( (16 , 200+32*i) , None , tiled=False)
        p.oriente( 0 )
        p.numero = nbAgentsCreated
        nbAgentsCreated = nbAgentsCreated + 1
        agents.append(AgentTypeA(p, w))

    for i in range(nbAgentsTypeB):
        p = game.add_players( (486 , 200+32*i) , None , tiled=False)
        p.oriente( 180 )
        p.numero = nbAgentsCreated
        nbAgentsCreated = nbAgentsCreated + 1
        agents.append(AgentTypeB(p))

    game.mainiteration()

def setupArena0():
    for i in range(6,13):
        addObstacle(row=3,col=i)
    for i in range(3,10):
        addObstacle(row=12,col=i)
    addObstacle(row=4,col=12)
    addObstacle(row=5,col=12)
    addObstacle(row=6,col=12)
    addObstacle(row=11,col=3)
    addObstacle(row=10,col=3)
    addObstacle(row=9,col=3)

def setupArena1():
    return

def setupArena2():
    for i in range(0,8):
        addObstacle(row=i,col=7)
    for i in range(8,16):
        addObstacle(row=i,col=8)

def updateSensors():
    global sensors 
    # throw_rays...(...) : appel couteux (une fois par itération du simulateur). permet de mettre à jour le masque de collision pour tous les robots.
    sensors = throw_rays_for_many_players(game,game.layers['joueur'],SensorBelt,max_radius = maxSensorDistance+game.player.diametre_robot() , show_rays=showSensors)

def stepWorld():
    efface()
    
    updateSensors()

    # chaque agent se met à jour. L'ordre de mise à jour change à chaque fois (permet d'éviter des effets d'ordre).
    shuffledIndexes = [i for i in range(len(agents))]
    shuffle(shuffledIndexes)
    for i in range(len(agents)):
        agents[shuffledIndexes[i]].step()
        # met à jour la grille d'occupation
        coord = agents[shuffledIndexes[i]].getRobot().get_centroid()
        occupancyGrid[int(coord[0])//16][int(coord[1])//16] = agents[shuffledIndexes[i]].getType() # first come, first served
    return


'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Fonctions internes   '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

def addObstacle(row,col):
    # le sprite situe colone 13, ligne 0 sur le spritesheet
    game.add_new_sprite('obstacle',tileid=(0,13),xy=(col,row),tiled=True)

class MyTurtle(Turtle): # also: limit robot speed through this derived class
    maxRotationSpeed = maxRotationSpeed # 10, 10000, etc.
    def rotate(self,a):
        mx = MyTurtle.maxRotationSpeed
        Turtle.rotate(self, max(-mx,min(a,mx)))

def displayOccupancyGrid():
    global iteration
    nbA = nbB = nothing = 0

    for y in range(screen_height//16):
        for x in range(screen_width//16):
            #sys.stdout.write(occupancyGrid[x][y])
            if occupancyGrid[x][y] == "A":
                nbA = nbA+1
            elif occupancyGrid[x][y] == "B":
                nbB = nbB+1
            else:
                nothing = nothing + 1
        #sys.stdout.write('\n')

#    sys.stdout.write('Time left: '+str(maxIterations-iteration)+'\n')
#    sys.stdout.write('Summary: \n')
#    sys.stdout.write('\tType A: ')
#    sys.stdout.write(str(nbA))
#    sys.stdout.write('\n')
#    sys.stdout.write('\tType B: ')
#    sys.stdout.write(str(nbB))
#    sys.stdout.write('\n')
#    sys.stdout.write('\tFree  : ')
#    sys.stdout.write(str(nothing))
#    sys.stdout.write('\n')
#    sys.stdout.flush() 

    return nbA,nbB,nothing

def onExit(filename = "out.txt"):
    ret = displayOccupancyGrid()
    with open(filename, "w") as file:
        file.write("{:d} {:d} {:d}".format(ret[0], ret[1], ret[2]))
    
#    print ("\n\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
#    if ret[0] > ret[1]:
#        print ("Robots type A (\"" + str(AgentTypeA.teamname) + "\") wins!")
#    elif ret[0] < ret[1]:
#        print ("Robots type B (\"" + str(AgentTypeB.teamname) + "\") wins!")
#    else: 
#        print ("Nobody wins!")
#    print ("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n")
#    print ("\n[Simulation::stop]")


'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Main loop            '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
with open("in.txt", "r") as file:
    line = file.readline()
    arena = int(line)
    line = file.readline()
    w = np.array([float(x) for x in line.split()])
    assert w.size==17

init('empty',MyTurtle,screen_width,screen_height) # display is re-dimensioned, turtle acts as a template to create new players/robots
game.auto_refresh = False # display will be updated only if game.mainiteration() is called
game.frameskip = frameskip
atexit.register(onExit)
 
if arena == 0:
    setupArena0()
elif arena == 1:
    setupArena1()
else:
    setupArena2()

setupAgents(w)

game.mainiteration()

def drawProgressBar(percent, barLen = 20):
    # percent float from 0 to 1. 
    sys.stdout.write("\r")
    sys.stdout.write("[{:<{}}] {:.0f}%".format("#" * int(barLen * percent), barLen, percent * 100))
    sys.stdout.flush()

iteration = 0
while iteration != maxIterations:
    if iteration % (maxIterations//100) == 0:
        drawProgressBar(iteration/maxIterations)
    stepWorld()
    game.mainiteration()
#    if iteration % 200 == 0:
#        displayOccupancyGrid()
    iteration = iteration + 1
onExit()
pygame.quit()
