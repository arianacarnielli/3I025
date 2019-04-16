    teamname = "NeverMind"

    def stepController(self):
        
        GO_FORWARD = 0
        AVOID_WALLS = 2
        FOLLOW_ENNEMY = 3
        AVOID_MATES = 4
        EXPLORE = 5
        ALONG_WALLS = 6
        STOP = 7
        TURN_RIGHT = 8
        
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
            diff = int( abs(orientation1-orientation2) )
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
        
        def only_sensors_detecting(type_array, sensors=[6]):
            for sensor in sensors:
                if type_array[sensor]!=1:
                    return False
            for i in range(8):
                if i in sensors:
                    continue
                if type_array[i]!=0:
                    return False
            return True
        
        
        # récupe des sensors
        dist_array = np.array([0.,0.,0.,0.,0.,0.,0.,0.])
        type_array = np.array([0.,0.,0.,0.,0.,0.,0.,0.])
        bot_info_list = [None]*8
        for i in range(8):
            dist_array[i] = 1 - self.getDistanceAtSensor(i)
            type_array[i] = self.getObjectTypeAtSensor(i)	
            bot_info_list[i] = self.getRobotInfoAtSensor(i)
   
    
#==============================================================================
#         Stratégie
#==============================================================================
        if self.id==2:
            comportement = ALONG_WALLS
            if only_sensors_detecting(type_array, sensors=[6]):
                comportement = GO_FORWARD
            comp_cpt = get_comp_cpt_from_etat()
            if comp_cpt > 2100:
                comportement = EXPLORE
            if comp_cpt > 5000:
                comportement = ALONG_WALLS
            if not an_enemy_is_detected(bot_info_list) and a_mate_is_detected(bot_info_list):
                comportement = AVOID_MATES
        else:
            comportement = EXPLORE


        # changer de comportement si bot ennemi (le suivre)
        if an_enemy_is_detected(bot_info_list):
            if not a_mate_is_detected(bot_info_list, sensors=[2,3,4,5]):
                comportement = FOLLOW_ENNEMY
                myOrientation = self.robot.orientation()
                otherOrientation = get_facing_enemy_orientation()
                if parallel_to_facing_enemy(myOrientation,otherOrientation):
                    comportement = AVOID_WALLS
        
        if self.id in [1,3]:
            comportement = EXPLORE
        
#==============================================================================
#         Évite les blocages en regardant la position
#==============================================================================        
        x0, y0, cpt, mode, comp_cpt = stateToVec(self.etat)
        x, y = self.robot.get_centroid()
        x = int(10*x)
        y = int(10*y)
        
        if mode not in [0,9] and comp_cpt%6==0 :
            if enemy_on_tail_detected(bot_info_list):
                mode += 1
                if mode>6:
                    mode = 8
            else:
                mode = 1
        
        if mode==8: # i am being followed --> stop any movement
            comportement = STOP
        
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
            
        elif mode==0: # drive backwards
            if cpt <= 0:
                mode = 1
            else:
                cpt -= 1
                color( (255,0,0) )
                circle( *self.getRobot().get_centroid() , r = 22)
                rotationValue = randint(-1,0)
                translationValue = -0.8
                if comportement==FOLLOW_ENNEMY:
                    rotationValue = -1
                    translationValue = -0.8
        
        if self.id==2 and comportement==ALONG_WALLS and only_sensors_detecting(type_array, sensors=[5]):
            if mode==1:
                mode = 9
                cpt = 20
        if mode==9:
            if cpt<=0:
                mode = 1
                comportement = ALONG_WALLS
            else:
                cpt -= 1
                comportement = TURN_RIGHT
        
        # make a 180* turn at the begining
        if self.id==2 and comp_cpt<40:
            comportement = TURN_RIGHT
        
        
        x0 = x
        y0 = y
        self.etat = vecToState(x0, y0, cpt, mode, comp_cpt+1)
        
        
        ### comportements
        if comportement == GO_FORWARD:
            rotationValue = 0
            translationValue = 1
            
        elif comportement == AVOID_WALLS:
            coefs = np.array([0., 0.2, 0.5, 0.7, -0.7, -0.5, -0.2, 0.])
            rotationValue = ( dist_array * (type_array%2) * coefs ).sum()
            translationValue = 1
            
        elif comportement == FOLLOW_ENNEMY:
            color( (169,169,169) )
            circle( *self.getRobot().get_centroid() , r = 22)
            coefs = np.array([0., -0.9, -0.6, -0.7, 0.7, 0.6, 0.9, 0.])
            rotationValue = (dist_array * (type_array//2) * coefs ).sum()
            translationValue = min(0.8+random(), 1)
            
        elif comportement == AVOID_MATES:
            color( (250,250,250) )
            circle( *self.getRobot().get_centroid() , r = 22)
            coefs = np.array([0., 0.2, 0.5, 0.7, -0.7, -0.5, -0.2, 0.])
            rotationValue = 0
            translationValue = -0.3
            
        elif comportement == EXPLORE:
            color( (238,130,238) )
            circle( *self.getRobot().get_centroid() , r = 22)
            coefs = np.array([0., 0.2, 0.5, 0.7, -0.7, -0.5, -0.2, 0.])
            rotationValue = (dist_array*type_array*coefs).sum() +0.39*(random()*2-1)
            translationValue = 1
            
        elif comportement == ALONG_WALLS:
            color( (255,255,0) )
            circle( *self.getRobot().get_centroid() , r = 22)
            ref = 0.41    #0.41   (0: away from wall - 1: near the wall)
            dif = 0.2     #2      (0: near the wall - 1: away from wall)
            coefs = np.array([[-0.9, 0., 0., 0., -0.7, -(ref+dif), ref, 0.9]])
            rotationValue = ( dist_array * (type_array%2) * coefs ).sum()
            translationValue = 1
            
        elif comportement==STOP:
            color( (0,0,0) )
            circle( *self.getRobot().get_centroid() , r = 22)
            rotationValue = 0
            translationValue = 0
            
        elif comportement == TURN_RIGHT:
            color( (0,0,200) )
            circle( *self.getRobot().get_centroid() , r = 22)
            rotationValue = 0.7
            translationValue = 1
        
        self.setRotationValue( rotationValue )
        self.setTranslationValue( translationValue )
        

        if verbose == True:
	        print ("Robot #"+str(self.id)+" [teamname:\""+str(self.teamname)+"\"] [variable mémoire = "+str(self.etat)+"] :")
	        for i in range(8):
	            print ("\tSenseur #"+str(i)+" (angle: "+ str(SensorBelt[i])+"°)")
	            print ("\t\tDistance  :",self.getDistanceAtSensor(i))
	            print ("\t\tType      :",self.getObjectTypeAtSensor(i)) # 0: nothing, 1: wall/border, 2: robot
	            print ("\t\tRobot info:",self.getRobotInfoAtSensor(i)) # dict("id","centroid(x,y)","orientation") (if not a robot: returns None and display a warning)
        return