#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#  python -m pip install pygame
#
# multirobot_teamwars.py
# Contact (ce fichier uniquement): nicolas.bredeche(type_array)upmc.fr
# Ce code utilise pySpriteWorld, développé par Yann Chevaleyre (U. Paris 13)
#
# Historique:
#   2016-03-28__23:23 - template pour 3i025 (IA&RO, UPMC, licence info)
#   2018-03-26__23:06 - mise à jour de l'énoncé du projet
#   2018-03-27__20:51 - reecriture de la fonction step(.)
# 	2018-03-28__10:00 - renommage de la fonction step(.) en stepController(.), refactoring
#   2019-04-02__11:42 - passage Python 3.x
#
# Description:
#   Template pour projet multi-robots "MULTIROBOT WARS"
#
#       But du jeu: posséder le maximum de cases!
#           Chaque joueur dispose de quatre robots
#           Le monde est divisé en 1024 cases (ie. 32x32 cases de 16x16 pixels)
#           Le jeu tourne pendant 4000 itérations
#           Une case "appartient" à la dernière équipe qui l'a visitée
#
#       Ce que vous avez le droit de faire:
#           Seules modifications autorisées:
#               la méthode stepController(.) de la classe AgentTypeA
#               la valeur de la variable teamname de la classe AgentTypeA
#               [!] tout autre modification est exclue!
#           Les vitesses de translation et rotation et les distances renvoyées par les senseurs sont normalisées
#               translation/rotation: entre -1 et +1
#               distance à l'obstacle: entre 0 et +1
#               En pratique, les valeurs réelles maximales sont fixées par maxTranslationSpeed et maxRotationSpeed et  maxSensorDistance.
#           Liste *exhaustive* des informations que vous pouvez utiliser (cf. fonction stepController(.)):
#               sur soi-même:
#                   son propre numéro [non modifiable]
#                   sa propre position (x,y) [non modifiable]
#                   sa propre orientation [non modifiable]
#                   son état [modifiable, type: entier -- exclusivement!]
#               sur les éléments détectés par les senseurs:
#                   distance à l'obstacle
#                   type d'obstacle (rien, mur, robot)
#                       si robot:
#                           son identifiant
#                           son orientation
#                           sa position (x,y)
#
#       Contrainte imposée:
#           Votre comportement doit être *réactif*.
#           C'est à dire pas de mémoire (pas de variable globale, pas de carte, etc.)
#           ...A la seule et unique exception donnée par la possibilité d'utiliser la variable entière "etat". (exemple d'utilisation: mémoriser l'occurence d'un évènement particulier, mémoriser le comportement utilisé à t-1, etc.)
#
#       Remarques:
#           La méthode stepController() de multirobots.py illustre les senseurs autorisés
#           Lors de l'évaluation, les numéros de vos robots peuvent être différents.
#           Vous pouvez utiliser teamname pour reconnaitre les robots appartenant à la votre équipe (ou à l'équipe adverse)
#           [!!!] les commandes de translation/rotation sont exécutées *après* la fonction stepController(.). Par conséquent, seules les valeurs passées lors du dernier appel des fonctions setTranslationValue(.) et setRotationValue(.) sont prises en compte!
#
#       Recommandations:
#           Conservez intact multirobot_teamwars.py (travaillez sur une copie!)
#           Pour faire vos tests, vous pouvez aussi modifier (si vous le souhaitez) la méthode stepController() pour la classe AgentTypeB. Il ne sera pas possible de transmettre cette partie là lors de l'évaluation par contre.
#           La manière dont vous construirez votre fonction stepController(.) est libre. Par exemple: code écrit à la main, code obtenu par un processus d'apprentissage ou d'optimisation préalable, etc.; comportements individuels, collectifs, parasites (p.ex: bloquer l'adversaire), etc.
#
#       Evaluation:
#           Soutenance devant machine (par binome, 15 min.) lors de la dernière séance de TP (matin et après-midi)
#               Vous devrez m'envoyer votre code et un PDF de 2 pages résumant vos choix d'implémentation. Sujet: "[3i025] binome1, binome2", la veille de la soutenance
#               Vous devrez montrer votre résultat sur plusieurs arènes inédites
#               Vous devrez mettre en évidence la réutilisation des concepts vus en cours
#               Vous devrez mettre en évidence les choix pragmatiques que vous avez du faire
#               Assurez vous que la simple copie de votre fonctions stepController(.) dans le fichier multirobots_teamwars.py suffit pour pouvoir le tester
#           Vous affronterez vos camarades
#               Au tableau: une matrice des combats a mettre a jour en fonction des victoires et défaites
#               Affrontement sur les trois arènes inédites
#               vous pouvez utiliser http://piratepad.net pour échanger votre fonction stepController(.))
#       Bon courage!
# 
# Dépendances:
#   Python 3.x
#   Matplotlib
#   Pygame
#
# Aide: code utile
#   - Partie "variables globales": en particulier pour définir le nombre d'agents et l'arène utilisée. La liste SensorBelt donne aussi les orientations des différentes capteurs de proximité.
#   - La méthode "step" de la classe Agent, la variable teamname.
#   - La fonction setupAgents (permet de placer les robots au début de la simulation) - ne pas modifier pour l'évaluation
#   - La fonction setupArena (permet de placer des obstacles au début de la simulation) - ne pas modifier pour l'évaluation. Cependant, cela peut-être très utile de faire des arènes originales.
#

from robosim import *
from random import random, shuffle, randint
import time
import sys
import atexit
import numpy as np
import math


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

maxIterations = 6000 # infinite: -1
showSensors = False
frameskip = 5  # 0: no-skip. >1: skip n-1 frames
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
'''  Agent "A"            '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

class AgentTypeA(object):
    
    agentIdCounter = 0 # use as static
    id = -1
    robot = -1
    agentType = "A"
    etat = 0
    
    translationValue = 0 # ne pas modifier directement
    rotationValue = 0 # ne pas modifier directement


    def __init__(self,robot):
        self.id = AgentTypeA.agentIdCounter
        AgentTypeA.agentIdCounter = AgentTypeA.agentIdCounter + 1
        #print ("robot #", self.id, " -- init")
        self.robot = robot
        self.robot.teamname = self.teamname

    def getType(self):
        return self.agentType

    def getRobot(self):
        return self.robot

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
        
        
        def a_mate_is_detected(bot_info_list, sensors=[2,3,4,5]):
            for i in sensors:
                if bot_info_list[i] is None:
                    continue
                if bot_info_list[i]['teamname'] == self.teamname:
                    return True
            return False
        
        def an_enemy_is_detected(bot_info_list, sensors=[1,2,3,4,5,6]):
            for i in sensors:
                if bot_info_list[i] is None:
                    continue
                if bot_info_list[i]['teamname'] != self.teamname:
                    return True
            return False
        
        def stateToVec(s):
            s, x = divmod(s, 10**5)
            s, y = divmod(s, 10**5)
            s, cpt = divmod(s, 10**2)
            s, mode = divmod(s, 10)
            return x, y, cpt, mode, s
        
        def vecToState(x, y, cpt, mode, comp):
            s = (10**13)*comp + (10**12)*mode + (10**10)*cpt + (10**5)*y + x
            return s
        
        def get_comp_cpt_from_etat():
            x, y, cpt, mode, comp = stateToVec(self.etat)
            return comp
        
        
        def enemy_on_tail_detected(bot_info_list):
            return an_enemy_is_detected(bot_info_list, sensors=[0,7])
        
        
        
        # récupe des sensors
        dist_array = np.array([0.,0.,0.,0.,0.,0.,0.,0.])
        type_array = np.array([0.,0.,0.,0.,0.,0.,0.,0.])
        bot_info_list = [None]*8
        for i in range(8):
            dist_array[i] = 1 - self.getDistanceAtSensor(i)
            type_array[i] = self.getObjectTypeAtSensor(i)	
            bot_info_list[i] = self.getRobotInfoAtSensor(i)
   
        ### stratégie
        
        if self.id==2:
            comportement = 6
            comp_cpt = get_comp_cpt_from_etat()
            if comp_cpt > 2200:
                comportement = 5
            if comp_cpt > 5000:
                comportement = 6
            if a_mate_is_detected(bot_info_list):
                comportement = 4
        else:
            comportement = 5
              
        # changer de comportement si bot ennemi (le suivre)
        if an_enemy_is_detected(bot_info_list):	# it's a bot
            if not a_mate_is_detected(bot_info_list, sensors=[2,3,4,5]):
                comportement = 3
        
        if self.id==3:
            comportement = 5
        
        
        
        ### comportements
        if comportement == 0:   # go straight forward
            rotationValue = 0
            translationValue = 1
        
        elif comportement == 1:   # go to walls
            coefs = np.array([0., -0.5, -0.5, -0.7, 0.7, 0.5, 0.5, 0.])
            rotationValue = ( dist_array * (type_array%2) * coefs ).sum()
            translationValue = 1
            
        elif comportement == 2:   # avoid walls
            coefs = np.array([0., 0.2, 0.5, 0.7, -0.7, -0.5, -0.2, 0.])
            rotationValue = ( dist_array * (type_array%2) * coefs ).sum()
            translationValue = 1
            
        elif comportement == 3:   # follow robots
            coefs = np.array([0., -0.9, -0.6, -0.7, 0.7, 0.6, 0.9, 0.])
            rotationValue = (dist_array * (type_array//2) * coefs ).sum()
            #translationValue = min(0.8+random(), 1)
            translationValue = min(0.8+random(), 1)
            
        elif comportement == 4:   # avoid robots
            coefs = np.array([0., 0.2, 0.5, 0.7, -0.7, -0.5, -0.2, 0.])
            rotationValue = 0
            translationValue = -0.3
        
        elif comportement == 5:   # avoid walls & robots
            coefs = np.array([0., 0.2, 0.5, 0.7, -0.8, -0.6, -0.3, 0.])
            rotationValue = (dist_array*type_array*coefs).sum() +0.39*(random()*2-1)
            translationValue = 1
        
        elif comportement == 6:   # follow walls
            ref = 0.3
            dif = 0.23     #23
            coefs = np.array([-0.3, ref, -(ref+dif), 0.4, -0.4, -(ref+dif), ref, 0.3])
            rotationValue = ( dist_array * (type_array%2) * coefs ).sum()
            translationValue = 1

        self.setRotationValue( rotationValue )
        self.setTranslationValue( translationValue )
        
        color( (0,255,0) )
        circle( *self.getRobot().get_centroid() , r = 22) # je dessine un rond vert autour de ce robot
        """
        

        # =============================================================================
        # Strategie
        # =============================================================================
        
# =============================================================================
#         middleId = nbAgents // 2 - 0.5
#         ar_dist = np.array([self.getDistanceAtSensor(i) for i in range(len(SensorBelt))])
#         ar_dist = 1 - ar_dist
#         ar_type = np.array([self.getObjectTypeAtSensor(i) for i in range(len(SensorBelt))])
#         ar_info = np.array([self.getRobotInfoAtSensor(i)["id"] if ar_type[i]==2 else middleId for i in range(ar_type.size)])
#         ar_info = np.sign((ar_info - middleId)*(self.robot.numero - middleId))
#         
#         sensors = np.empty(2*ar_dist.size + 1)
#         sensors[0] = 1
#         sensors[1:(ar_dist.size+1)] = ar_dist * (ar_type % 2)
#         sensors[(ar_dist.size+1):] = ar_dist * ar_info
#         
#         rot_val = np.dot(ar_dist[1:7] * (ar_type[1:7]!=0), [1, 1, 1, -1, -1, -1])
#         
#         #rot_val = np.dot(ar_dist[2:6], ar_type[2:6])
#     
#         self.setRotationValue(rot_val + 0.2*random()-0.1)
#         self.setTranslationValue(1) # normalisé -1,+1
#         
#         if ar_type.sum() == 0:
#             self.setRotationValue((random() > 0.5) * 2 - 1)
# =============================================================================
            
# =============================================================================
# Algo genetique
# =============================================================================
# =============================================================================
             
        w = np.array([0., 1., 1., 1., -1., -1., -0.5, 0.5, -0.75, 1., 1., 1., -1., -1., -1., 0., 0., -0.25, 1., 1., -1., -1., -1., 0., 0.])
        #w = np.array([ 0.  ,  1.  ,  1.  ,  1.  , -1.  , -1.  , -0.5 ,  0.5 , -0.8,  1.  ,  1.  ,  1.  , -1.  , -1.  , -1.  ,  0.  ,  0.  , -0.2,  1.  ,  1.  , -1.  , -1.  , -1.  ,  0.  ,  0.  ])
    
        N = len(SensorBelt)
        middleId = nbAgents // 2 - 0.5
        ar_dist = np.array([self.getDistanceAtSensor(i) for i in range(N)])
        ar_dist = 1 - ar_dist
        ar_type = np.array([self.getObjectTypeAtSensor(i) for i in range(N)])
        ar_info = np.array([self.getRobotInfoAtSensor(i)["id"] if ar_type[i]==2 else middleId for i in range(N)])
        ar_info = np.sign((ar_info - middleId)*(self.robot.numero - middleId))
        
        sensors = np.empty(3*N + 1)
        sensors[-1] = 1
        sensors[:N] = ar_dist * (ar_type % 2)
        sensors[N:(2*N)] = ar_dist * (ar_info==1)
        sensors[(2*N):(3*N)] = ar_dist * (ar_info==-1)
        
        self.setRotationValue(min(1, max(-1, w.dot(sensors) + 0.2*random() - 0.1)))
        self.setTranslationValue(1)
        
        if ar_type.sum() == 0:
            self.setRotationValue((random() > 0.5) * 2 - 1)
# =============================================================================
    
#==============================================================================
#         Évite les blocages en regardant la position
#==============================================================================        
        def stateToVec(s):
            s, x = divmod(s, 10**5)
            s, y = divmod(s, 10**5)
            s, cpt = divmod(s, 10**2)
            return x, y, cpt, s
            
        def vecToState(x, y, cpt, mode):
            s = (10**12)*mode + (10**10)*cpt + (10**5)*y + x
            return s
        
        x0, y0, cpt, mode = stateToVec(self.etat)
        x, y = self.robot.get_centroid()
        x = int(10*x)
        y = int(10*y)
        
        if mode==0:
            if abs(x - x0) + abs(y - y0) <= 2:
                if cpt >= 60:
                    mode = 1
                else:
                    cpt += 1
            else:
                pass
        else:
            if cpt <= 0:
                mode = 0
            else:
                cpt -= 1
                self.setRotationValue((random() > 0.5)*2 - 1)
                self.setTranslationValue(-1)
                
        x0 = x
        y0 = y
        self.etat = vecToState(x0, y0, cpt, mode)
#==============================================================================
#         Évite les blocages en regardant les capteurs        
#==============================================================================
#==============================================================================
#         def stateToVec(s, bits = 6, size = 8):
#             vec = np.empty(size, dtype=int)
#             for i in range(size-1, -1, -1):
#                 s, vec[i] = divmod(s, 2**bits)
#             return vec, s
#         
#         def vecToState(vec, mode, bits = 6):
#             gambiarra = 2**100
#             s = gambiarra + mode
#             for i in range(vec.size):
#                 s = (s << bits) + (vec[i] % (2**bits))
#                 gambiarra = (gambiarra << bits)
#             return s - gambiarra
#         
#         vec, mode = stateToVec(self.etat)
#         #print(vec, mode)
#         if mode == 1:
#             if np.all(vec == 0):
#                 mode = 0
#             else:
#                 vec -= 1
#                 self.setRotationValue((random() * 2) - 1)
#                 self.setTranslationValue(-1)
#         else:
#             if (vec >= 60).sum() >= 2:
#                 mode = 1
#                 vec[:] = 60
#             else:
#                 vec[ar_type != 0] += 1
#         #print(vec, mode)
#         self.etat = vecToState(np.minimum(vec, 60), mode)
#==============================================================================
        """
		# monitoring (optionnel - changer la valeur de verbose)
        if verbose == True:
	        print ("Robot #"+str(self.id)+" [teamname:\""+str(self.teamname)+"\"] [variable mémoire = "+str(self.etat)+"] :")
	        for i in range(len(SensorBelt)):
	            print ("\tSenseur #"+str(i)+" (angle: "+ str(SensorBelt[i])+"°)")
	            print ("\t\tDistance  :",self.getDistanceAtSensor(i))
	            print ("\t\tType      :",self.getObjectTypeAtSensor(i)) # 0: rien, 1: mur ou bord, 2: robot
	            print ("\t\tRobot info:",self.getRobotInfoAtSensor(i)) # dict("id","centroid(x,y)","orientation") (si pas de robot: renvoi "None" et affiche un avertissement dans la console

        return

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
            #print ("[WARNING] translation value not in [-1,+1]. Normalizing.")
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
'''  Agent "B"            '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

class AgentTypeB(object):
    
    agentIdCounter = 0 # use as static
    id = -1
    robot = -1
    agentType = "B"
    etat = 0
    
    translationValue = 0
    rotationValue = 0

    def __init__(self,robot):
        self.id = AgentTypeB.agentIdCounter
        AgentTypeB.agentIdCounter = AgentTypeB.agentIdCounter + 1
        #print ("robot #", self.id, " -- init")
        self.robot = robot
        self.robot.teamname = self.teamname


    def getType(self):
        return self.agentType

    def getRobot(self):
        return self.robot


    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-= JOUEUR B -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    teamname = "Dave" # A modifier avec le nom de votre équipe

    def stepController(self):
        
        def a_mate_is_detected(bot_info_list, sensors=[2,3,4,5]):
            for i in sensors:
                if bot_info_list[i] is None:
                    continue
                if bot_info_list[i]['teamname'] == self.teamname:
                    return True
            return False
        
        def an_enemy_is_detected(bot_info_list, sensors=[1,2,3,4,5,6]):
            for i in sensors:
                if bot_info_list[i] is None:
                    continue
                if bot_info_list[i]['teamname'] != self.teamname:
                    return True
            return False
        
        def get_facing_enemy_orientation(sensors=[1,2,3,4,5,6]):
            for i in sensors:
                if bot_info_list[i] is None:
                    continue
                return bot_info_list[i]['orientation']
        
        def parallel_to_facing_enemy(orientation1, orientation2, d=15):
            diff = int( math.fabs(orientation1-orientation2) )
            return diff in range(180-d,180+d)
        
        def stateToVec(s):
            s, x = divmod(s, 10**5)
            s, y = divmod(s, 10**5)
            s, cpt = divmod(s, 10**2)
            s, mode = divmod(s, 10)
            return x, y, cpt, mode, s
        
        def vecToState(x, y, cpt, mode, comp):
            s = (10**13)*comp + (10**12)*mode + (10**10)*cpt + (10**5)*y + x
            return s
        
        def get_comp_cpt_from_etat():
            x, y, cpt, mode, comp = stateToVec(self.etat)
            return comp
        
        def enemy_on_tail_detected(bot_info_list):
            return an_enemy_is_detected(bot_info_list, sensors=[0,7])
        
        
        # récupe des sensors
        dist_array = np.array([0.,0.,0.,0.,0.,0.,0.,0.])
        type_array = np.array([0.,0.,0.,0.,0.,0.,0.,0.])
        bot_info_list = [None]*8
        for i in range(8):
            dist_array[i] = 1 - self.getDistanceAtSensor(i)
            type_array[i] = self.getObjectTypeAtSensor(i)	
            bot_info_list[i] = self.getRobotInfoAtSensor(i)
   
    
        ### stratégie
        if self.id==2:
            comportement = 6
            comp_cpt = get_comp_cpt_from_etat()
            if comp_cpt > 2100:
                comportement = 5
            if comp_cpt > 5000:
                comportement = 6
            if not an_enemy_is_detected(bot_info_list) and a_mate_is_detected(bot_info_list):
                comportement = 4
        else:
            comportement = 5
              
            
        # changer de comportement si bot ennemi (le suivre)
        if an_enemy_is_detected(bot_info_list):	# it's a bot
            if not a_mate_is_detected(bot_info_list, sensors=[2,3,4,5]):
                comportement = 3
                myOrientation = self.robot.orientation()
                otherOrientation = get_facing_enemy_orientation()
                if parallel_to_facing_enemy(myOrientation,otherOrientation):
                    comportement = 2
        
        if self.id in [1,3]:
            comportement = 5
        
        
        # coloration
        if comportement==3:
            color( (169,169,169) )
            circle( *self.getRobot().get_centroid() , r = 22)
        elif comportement==4:
            color( (250,250,250) )
            circle( *self.getRobot().get_centroid() , r = 22)
        elif comportement==5:
            color( (238,130,238) )
            circle( *self.getRobot().get_centroid() , r = 22)
        elif comportement==6:
            color( (255,255,0) )
            circle( *self.getRobot().get_centroid() , r = 22)
        
        
        ### comportements
        if comportement == 0:   # go straight forward
            rotationValue = 0
            translationValue = 1
        elif comportement == 1:   # go to walls
            coefs = np.array([0., -0.5, -0.5, -0.7, 0.7, 0.5, 0.5, 0.])
            rotationValue = ( dist_array * (type_array%2) * coefs ).sum()
            translationValue = 1
        elif comportement == 2:   # avoid walls
            coefs = np.array([0., 0.2, 0.5, 0.7, -0.7, -0.5, -0.2, 0.])
            rotationValue = ( dist_array * (type_array%2) * coefs ).sum()
            translationValue = 1
        elif comportement == 3:   # follow robots
            coefs = np.array([0., -0.9, -0.6, -0.7, 0.7, 0.6, 0.9, 0.])
            rotationValue = (dist_array * (type_array//2) * coefs ).sum()
            translationValue = min(0.8+random(), 1)
        elif comportement == 4:   # avoid robots
            coefs = np.array([0., 0.2, 0.5, 0.7, -0.7, -0.5, -0.2, 0.])
            rotationValue = 0
            translationValue = -0.3
        elif comportement == 5:   # avoid walls & robots
            coefs = np.array([0., 0.2, 0.5, 0.7, -0.8, -0.6, -0.3, 0.])
            rotationValue = (dist_array*type_array*coefs).sum() +0.39*(random()*2-1)
            translationValue = 1
        elif comportement == 6:   # follow walls
            ref = 0.3
            dif = 0.23     #23
            coefs = np.array([-0.3, ref, -(ref+dif), 0.4, -0.4, -(ref+dif), ref, 0.3])
            rotationValue = ( dist_array * (type_array%2) * coefs ).sum()
            translationValue = 1
        
        
#==============================================================================
#         Évite les blocages en regardant la position
#==============================================================================        
        x0, y0, cpt, mode, comp_cpt = stateToVec(self.etat)
        x, y = self.robot.get_centroid()
        x = int(10*x)
        y = int(10*y)
        
        
        if mode!=0 and comp_cpt%6==0 :
            if enemy_on_tail_detected(bot_info_list):
                mode += 1
                if mode>6:
                    mode = 9
            else:
                mode = 1
        
        if mode==9: # i am being followed --> stop any movement
            comportement = 7
        
        elif comportement not in [2,7] and mode==1: # normal mode
            if abs(x - x0) + abs(y - y0) <= 2:
                if cpt >= 36:
                    mode = 0    # drive backwards
                    cpt = 26
                else:
                    cpt += 1
            else:
                cpt = 0
                pass
            
        elif mode==0: # reverse mode
            if cpt <= 0:
                mode = 1
            else:
                cpt -= 1
                color( (255,0,0) )
                circle( *self.getRobot().get_centroid() , r = 22)
                rotationValue = randint(-1,0)
                translationValue = -0.8
                if comportement==3:
                    cpt -= 1
                    rotationValue = -1
                    translationValue = -0.7
                
        x0 = x
        y0 = y
        self.etat = vecToState(x0, y0, cpt, mode, comp_cpt+1)
        
        
        
        if comportement==7: # stop any movement
            rotationValue = 0
            translationValue = 0
            color( (0,0,0) )
            circle( *self.getRobot().get_centroid() , r = 22)
        
        
        self.setRotationValue( rotationValue )
        self.setTranslationValue( translationValue )
        
		# monitoring (optionnel - changer la valeur de verbose)
        if verbose == True:
	        print ("Robot #"+str(self.id)+" [teamname:\""+str(self.teamname)+"\"] [variable mémoire = "+str(self.etat)+"] :")
	        for i in range(8):
	            print ("\tSenseur #"+str(i)+" (angle: "+ str(SensorBelt[i])+"°)")
	            print ("\t\tDistance  :",self.getDistanceAtSensor(i))
	            print ("\t\tType      :",self.getObjectTypeAtSensor(i)) # 0: nothing, 1: wall/border, 2: robot
	            print ("\t\tRobot info:",self.getRobotInfoAtSensor(i)) # dict("id","centroid(x,y)","orientation") (if not a robot: returns None and display a warning)

        return

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
            #print ("[WARNING] translation value not in [-1,+1]. Normalizing.")
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
'''  Fonctions init/step  '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''


def setupAgents():
    global screen_width, screen_height, nbAgents, agents, game

    # Make agents

    nbAgentsTypeA = nbAgentsTypeB = nbAgents // 2
    nbAgentsCreated = 0

    for i in range(nbAgentsTypeA):
        p = game.add_players( (16 , 200+32*i) , None , tiled=False)
        p.oriente( 0 )
        p.numero = nbAgentsCreated
        nbAgentsCreated = nbAgentsCreated + 1
        agents.append(AgentTypeA(p))

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

def setupArena3():
    w = screen_width//32
    h = screen_height//32
    for i in range(h):
        if i==h//4:
            continue
        addObstacle(row=i,col=w//2)
        addObstacle(row=i,col=w//2-1)
    
def setupArena4():
    hlist = [
             [3,[4,5,6,7,8,9,10,11]],
             [6,[4,5,6,7,8]],
             [9,[7,8,9,10,11]],
             [12,[4,5,6,7,8,9,10,11]]
            ]
    vlist = [
             [4,[7,8,9,10,11]],
             [11,[4,5,6,7,8]],
            ]
    for l in hlist:
        lig = l[0]
        col_list = l[1]
        for col in col_list:
            addObstacle(row=lig,col=col)
    
    for l in vlist:
        col = l[0]
        lig_list = l[1]
        for lig in lig_list:
            addObstacle(row=lig,col=col)
    return
    

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
            sys.stdout.write(occupancyGrid[x][y])
            if occupancyGrid[x][y] == "A":
                nbA = nbA+1
            elif occupancyGrid[x][y] == "B":
                nbB = nbB+1
            else:
                nothing = nothing + 1
        sys.stdout.write('\n')

    sys.stdout.write('Time left: '+str(maxIterations-iteration)+'\n')
    sys.stdout.write('Summary: \n')
    sys.stdout.write('\tType A: ')
    sys.stdout.write(str(nbA))
    sys.stdout.write('\n')
    sys.stdout.write('\tType B: ')
    sys.stdout.write(str(nbB))
    sys.stdout.write('\n')
    sys.stdout.write('\tFree  : ')
    sys.stdout.write(str(nothing))
    sys.stdout.write('\n')
    sys.stdout.flush() 

    return nbA,nbB,nothing

def onExit():
    ret = displayOccupancyGrid()
    print ("\n\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    if ret[0] > ret[1]:
        print ("Robots type A (\"" + str(AgentTypeA.teamname) + "\") wins!")
    elif ret[0] < ret[1]:
        print ("Robots type B (\"" + str(AgentTypeB.teamname) + "\") wins!")
    else: 
        print ("Nobody wins!")
    print ("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n")
    print ("\n[Simulation::stop]")


'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Main loop            '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

init('empty',MyTurtle,screen_width,screen_height) # display is re-dimensioned, turtle acts as a template to create new players/robots
game.auto_refresh = False # display will be updated only if game.mainiteration() is called
game.frameskip = frameskip
atexit.register(onExit)

if arena == 0:
    setupArena0()
elif arena == 1:
    setupArena1()
elif arena == 2:
    setupArena2()
elif arena == 3:
    setupArena3()
else:
    setupArena4()

setupAgents()
game.mainiteration()

iteration = 0
while iteration != maxIterations:
    stepWorld()
    game.mainiteration()
    if iteration % 200 == 0:
        displayOccupancyGrid()
    iteration = iteration + 1

