# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 04:06:31 2019

@author: arian
"""

        FOLLOW = 0
        EXPLORE = 1
        DEVIATE = 2
        
        
        
        # Pour utiliser cette statégie en dehors de l'algo génétique.
        if self.id==0 or self.id==1:
           self.w = np.array( [8.00000000e+01,  1.10000000e+02, -5.00000000e-01,  4.00000000e-01,
        7.00000000e-01,  7.00000000e-01,  8.00000000e-01,  5.00000000e-01,
       -3.00000000e-01, -6.00000000e-01,  0.00000000e+00, -8.00000000e-01,
        3.00000000e-01,  1.00000000e-01, -7.00000000e-01, -1.00000000e+00,
       -2.00000000e-01,  1.00000000e+00, -9.00000000e-01,  8.00000000e-01,
        1.00000000e-01, -2.00000000e-01])
        else:
            self.w = np.array([3.00000000e+01,  1.10000000e+02,
        1.00000000e+00,  2.00000000e-01,  6.00000000e-01, -2.22044605e-16,
       -7.00000000e-01, -2.00000000e-01, -9.00000000e-01,  0.00000000e+00,
        6.00000000e-01,  5.00000000e-01,  4.00000000e-01, -6.00000000e-01,
       -7.00000000e-01, -3.00000000e-01, -1.00000000e+00,  9.00000000e-01,
       -7.00000000e-01,  5.00000000e-01,  0.00000000e+00, -8.00000000e-01])
            
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
            color((238, 238, 130))
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
        