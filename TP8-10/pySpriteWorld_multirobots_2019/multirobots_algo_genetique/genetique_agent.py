# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 19:44:46 2019

@author: arian
"""

import numpy as np

from random import random
from robosim import color, circle

#==============================================================================
# Agent générique
#==============================================================================
class Agent(object):
    agentIdCounter = 0 # use as static
    id = -1
    robot = -1
    agentType = "X"
    etat = 0
    
    translationValue = 0 # ne pas modifier directement
    rotationValue = 0 # ne pas modifier directement

    def __init__(self, robot, jeu):
        self.robot = robot
        self.robot.teamname = self.teamname
        self.jeu = jeu

    def getType(self):
        return self.agentType

    def getRobot(self):
        return self.robot

    teamname = "Agent"

    def stepController(self):
        pass

    def step(self):
        self.stepController()
        self.move()

    def move(self):
        self.robot.forward(self.translationValue)
        self.robot.rotate(self.rotationValue)

    def getDistanceAtSensor(self,id):
        sensor_infos = self.jeu.sensors[self.robot] # sensor_infos est une liste de namedtuple (un par capteur).
        return min(sensor_infos[id].dist_from_border,self.jeu.maxSensorDistance) / self.jeu.maxSensorDistance

    def getObjectTypeAtSensor(self,id):
        if self.jeu.sensors[self.robot][id].dist_from_border > self.jeu.maxSensorDistance:
            return 0 # nothing
        elif self.jeu.sensors[self.robot][id].layer == 'joueur':
            return 2 # robot
        else:
            return 1 # wall/border

    def getRobotInfoAtSensor(self,id):
        if self.jeu.sensors[self.robot][id].dist_from_border < self.jeu.maxSensorDistance and self.jeu.sensors[self.robot][id].layer == 'joueur':
            otherRobot = self.jeu.sensors[self.robot][id].sprite
            info = {'id': otherRobot.numero, 'centroid': otherRobot.get_centroid(), 'orientation': otherRobot.orientation(), 'teamname': otherRobot.teamname }
            return info
        else:
            #print ("[WARNING] getPlayerInfoAtSensor(.): not a robot!")
            return None

    def setTranslationValue(self,value):
        if value > 1:
            #♠print ("[WARNING] translation value not in [-1,+1]. Normalizing.")
            value = self.jeu.maxTranslationSpeed
        elif value < -1:
            #print ("[WARNING] translation value not in [-1,+1]. Normalizing.")
            value = -self.jeu.maxTranslationSpeed
        else:
            value = value * self.jeu.maxTranslationSpeed
        self.translationValue = value

    def setRotationValue(self,value):
        if value > 1:
            #print ("[WARNING] translation value not in [-1,+1]. Normalizing.")
            value = self.jeu.maxRotationSpeed
        elif value < -1:
            #print ("[WARNING] translation value not in [-1,+1]. Normalizing.")
            value = - self.jeu.maxRotationSpeed
        else:
            value = value * self.jeu.maxRotationSpeed
        self.rotationValue = value

#==============================================================================
# Agent A
#==============================================================================
class AgentTypeA(Agent):
    agentType = "A"
    teamname = "AAAH" # A modifier avec le nom de votre équipe

    def __init__(self, robot, jeu, w):
        super().__init__(robot, jeu)
        self.id = AgentTypeA.agentIdCounter
        AgentTypeA.agentIdCounter = AgentTypeA.agentIdCounter + 1
        self.w = w
        #print ("robot #", self.id, " -- init")

    def stepController(self):    
        verbose = self.jeu.verbose
        SensorBelt = self.jeu.SensorBelt
 
        FOLLOW = 0
        EXPLORE = 1
        DEVIATE = 2
        
        # Pour utiliser cette statégie en dehors de l'algo génétique.
#        if self.id==0 or self.id==1:
#            self.w = np.array([60,
#                               90,
#                               0., 0.2, 0.5, 0.7, -0.8, -0.6, -0.3, 0.,
#                               1,
#                               0., -0.9, -0.6, -0.7, 0.7, 0.6, 0.9, 0.,
#                               0.8,
#                               1,
#                               0])
#        else:
#            self.w = np.array([60,
#                               90,
#                               0., 0.2, 0.5, 0.7, -0.8, -0.6, -0.3, 0.,
#                               1,
#                               0., -0.9, -0.6, -0.7, 0.7, 0.6, 0.9, 0.,
#                               0.8,
#                               1,
#                               0])
            
        cptReverse = self.w[0]
        angleFollow = self.w[1]
        coefExplore = self.w[2:10]
        coefExploreNoise = self.w[10]
        coefFollow = self.w[11:19]
        coefFollowTranslation = self.w[19]
        coefDeviateRotation = self.w[20]
        coefDeviateTranslation = self.w[21]
        
        def a_mate_is_detected(bot_info_list, sensors=[2,3,4,5]):
            for i in sensors:
                if bot_info_list[i] is None:
                    continue
                if bot_info_list[i]['teamname'] == self.teamname:
                    return bot_info_list[i]
            return False
        
        def an_enemy_is_detected(bot_info_list, sensors=[1,2,3,4,5,6]):
            for i in sensors:
                if bot_info_list[i] is None:
                    continue
                if bot_info_list[i]['teamname'] != self.teamname:
                    return bot_info_list[i]
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

        def reverse(x0, y0, cpt, mode, x, y):
            if mode==0:
                if abs(x - x0) + abs(y - y0) <= 2:
                    if cpt >=cptReverse:
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
                    color((255,0,0))
                    circle(*self.getRobot().get_centroid(), r = 22)
                    self.setRotationValue((random() > 0.5)*2 - 1)
                    self.setTranslationValue(-1)
            return mode, cpt
        
        # récupe des sensors
        dist_array = np.empty(8)
        type_array = np.empty(8)
        bot_info_list = np.empty(8, dtype=object)
        for i in range(8):
            dist_array[i] = 1 - self.getDistanceAtSensor(i)
            type_array[i] = self.getObjectTypeAtSensor(i)	
            bot_info_list[i] = self.getRobotInfoAtSensor(i)
        #print(bot_info_list)
        
        # récuèpre les infos de l'état
        x0, y0, cpt, mode, comp_enemyBehind = stateToVec(self.etat)
        x, y =  self.robot.get_centroid()
        x = int(10*x)
        y = int(10*y)
        
        ### arbre de décision
        enemyFront = an_enemy_is_detected(bot_info_list)
        enemyBehind = an_enemy_is_detected(bot_info_list, sensors = [0, 7])
        if enemyBehind is not False:
            comportement = DEVIATE
        else:
            if enemyFront is not False:
                mate = a_mate_is_detected(bot_info_list)
                diffAngle = abs(enemyFront["orientation"] - self.robot.orientation())
                if mate is not False:
                    if mate["id"] < self.robot.numero:  
                        if abs(diffAngle - 180) <= angleFollow:
                            comportement = EXPLORE
                        else:
                            comportement = FOLLOW
                    else:
                        comportement = EXPLORE
                else:
                    if abs(diffAngle - 180) <= angleFollow:
                        comportement = EXPLORE
                    else:
                        comportement = FOLLOW
            else:
                comportement = EXPLORE
        
        # Implémentation des stratégies
        if comportement == EXPLORE:
            color((238, 130, 238))
            circle(*self.getRobot().get_centroid(), r = 22)
            #coefs = np.array([0., 0.2, 0.5, 0.7, -0.8, -0.6, -0.3, 0.])
            coefs = coefExplore
            self.setRotationValue(coefs.dot(dist_array * (type_array > 0)) + coefExploreNoise * (((random() > 0.5) * 2) - 1))
            self.setTranslationValue(1)
            mode, cpt = reverse(x0, y0, cpt, mode, x, y)
        elif comportement == FOLLOW:
            color((169, 169, 169))
            circle(*self.getRobot().get_centroid(), r = 22)
            #coefs = np.array([0., -0.9, -0.6, -0.7, 0.7, 0.6, 0.9, 0.])
            coefs = coefFollow
            self.setRotationValue(coefs.dot(dist_array * (type_array//2)))
            self.setTranslationValue(min(coefFollowTranslation + random(), 1))
            mode, cpt = reverse(x0, y0, cpt, mode, x, y)
        elif comportement == DEVIATE:
            color((0, 169, 0))
            circle(*self.getRobot().get_centroid(), r = 22)
            self.setRotationValue(coefDeviateRotation * ((random() > 0.5) * 2 - 1))
            self.setTranslationValue(coefDeviateTranslation)
            
        x0 = x
        y0 = y
        self.etat = vecToState(x0, y0, cpt, mode, comp_enemyBehind)
        if verbose == True:
	        print ("Robot #"+str(self.id)+" [teamname:\""+str(self.teamname)+"\"] [variable mémoire = "+str(self.etat)+"] :")
	        for i in range(8):
	            print ("\tSenseur #"+str(i)+" (angle: "+ str(SensorBelt[i])+"°)")
	            print ("\t\tDistance  :",self.getDistanceAtSensor(i))
	            print ("\t\tType      :",self.getObjectTypeAtSensor(i)) # 0: nothing, 1: wall/border, 2: robot
	            print ("\t\tRobot info:",self.getRobotInfoAtSensor(i)) # dict("id","centroid(x,y)","orientation") (if not a robot: returns None and display a warning)
        
    def setW(self, w):
        self.w = w
#==============================================================================
# Agent B
#==============================================================================
class AgentTypeB(Agent):
    agentType = "B"
    teamname = "Equipe Test" # A modifier avec le nom de votre équipe
    
    def __init__(self, robot, jeu, nb):
        super().__init__(robot, jeu)
        self.id = AgentTypeB.agentIdCounter
        AgentTypeB.agentIdCounter = AgentTypeB.agentIdCounter + 1
        self.nb = nb
        self.jeu = jeu
        #print ("robot #", self.id, " -- init")
        
    def stepController(self):
        
        color((0, 0, 255))
        circle(*self.getRobot().get_centroid(), r = 22)
        verbose = self.jeu.verbose
        SensorBelt = self.jeu.SensorBelt
        
        from random import randint
        
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
        
        
        if self.nb == 0:

            ### stratégies
            
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
    
            self.setRotationValue(rotationValue)
            self.setTranslationValue( translationValue )
            
            color((0,255,0))
            circle(*self.getRobot().get_centroid(), r = 22) # je dessine un rond vert autour de ce robot
            
        elif self.nb == 1:  
       
            ### stratégies
            
            if self.id==0:
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
            
            if self.id==2:
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
                translationValue = -0.2
            
            elif comportement == 5:   # avoid walls & robots
                coefs = np.array([0., 0.2, 0.5, 0.7, -0.8, -0.6, -0.3, 0.])
                rotationValue = (dist_array*type_array*coefs).sum() +0.3*randint(-1,1)
                translationValue = 1
            
            elif comportement == 6:   # follow walls
                ref = 0.3
                dif = 0.23     #23
                coefs = np.array([-0.3, ref, -(ref+dif), 0.4, -0.4, -(ref+dif), ref, 0.3])
                rotationValue = ( dist_array * (type_array%2) * coefs ).sum()
                translationValue = 1
    
            self.setRotationValue( rotationValue )
            self.setTranslationValue( translationValue )
            
    #==============================================================================
    #         Évite les blocages en regardant la position
    #==============================================================================        
            x0, y0, cpt, mode, comp_cpt = stateToVec(self.etat)
            x, y = self.robot.get_centroid()
            x = int(10*x)
            y = int(10*y)
            
            if mode==0:
                if abs(x - x0) + abs(y - y0) <= 2:
                    if cpt >= 36:
                        mode = 1
                        cpt = 30
                    else:
                        cpt += 1
                else:
                    cpt = 0
                    pass
            else:
                if cpt <= 0:
                    mode = 0
                else:
                    cpt -= 1
                    rotationValue = randint(-1,0)
                    translationValue = -0.8
                    if comportement==3:
                        rotationValue=0
                        translationValue=-0.3
                    self.setRotationValue(rotationValue)
                    self.setTranslationValue(translationValue)
                    
            x0 = x
            y0 = y
            self.etat = vecToState(x0, y0, cpt, mode, comp_cpt+1)
        
        elif self.nb == 2: 
                    
            w = np.array([0., 1., 1., 1., -1., -1., -0.5, 0.5, -0.75, 1., 1., 1., -1., -1., -1., 0., 0., -0.25, 1., 1., -1., -1., -1., 0., 0.])
            #w = np.array([ 0.  ,  1.  ,  1.  ,  1.  , -1.  , -1.  , -0.5 ,  0.5 , -0.8,  1.  ,  1.  ,  1.  , -1.  , -1.  , -1.  ,  0.  ,  0.  , -0.2,  1.  ,  1.  , -1.  , -1.  , -1.  ,  0.  ,  0.  ])
        
            N = len(SensorBelt)
            middleId = self.jeu.nbAgents // 2 - 0.5
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
                    if cpt >= 30:
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
        
		# monitoring (optionnel - changer la valeur de verbose)
        if verbose == True:
	        print ("Robot #"+str(self.id)+" [teamname:\""+str(self.teamname)+"\"] [variable mémoire = "+str(self.etat)+"] :")
	        for i in range(8):
	            print ("\tSenseur #"+str(i)+" (angle: "+ str(SensorBelt[i])+"°)")
	            print ("\t\tDistance  :",self.getDistanceAtSensor(i))
	            print ("\t\tType      :",self.getObjectTypeAtSensor(i)) # 0: nothing, 1: wall/border, 2: robot
	            print ("\t\tRobot info:",self.getRobotInfoAtSensor(i)) # dict("id","centroid(x,y)","orientation") (if not a robot: returns None and display a warning)

        return