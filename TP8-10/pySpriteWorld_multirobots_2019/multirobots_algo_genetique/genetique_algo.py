# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 20:03:33 2019

@author: arian
"""

import numpy as np
from genetique_jeu import game, Jeu

class AlgoGenetique:
    def __init__(self, nbPopulation, nbFeatures, mutation,\
                 pGood, pBad, pRandom,\
                 n, nbArenas, en, filename = None):
        self.fromFile = False
        if filename is not None:
            self.fromFile = True
            with np.load(filename) as file:
                self.w = file["w"]
                self.mutation = file["mutation"][0]
                self.nbPopulation, self.nbFeatures = self.w.shape
                self.nbFeatures = self.nbFeatures // 2
                self.results = file["results"]
        else:
            self.nbPopulation = nbPopulation
            self.mutation = mutation
            self.nbFeatures = nbFeatures
            self.w = np.empty((self.nbPopulation, 2*self.nbFeatures))
            for i in range(self.nbPopulation):
                self.w[i, :] = self.wRowRandom()
            self.results = np.zeros(self.nbPopulation, dtype=int)
        self.nbGood = int(pGood*self.nbPopulation)
        self.nbBad = int(pBad*self.nbPopulation)
        self.nbRandom = int(pRandom*self.nbPopulation)
        assert self.nbGood > 0 and self.nbGood+self.nbBad+self.nbRandom < self.nbPopulation
        self.n = n
        self.en = en
        self.nbArenas = nbArenas
        self.jeu = Jeu(maxIterations = 4000, nbAgents = 8, game = game)
        
    def save(self, filename):
        np.savez(filename, w = self.w, mutation = np.array([self.mutation]), results = self.results)

#    def sendWToSimul(wRow, arena, filename = "in.txt"):
#        with open(filename, "w") as file:
#            file.write("{:d}\n".format(arena))
#            string = " ".join(["{:.4f}".format(e) for e in wRow])
#            file.write(string)
#    
#    def getResultFromSimul(filename = "out.txt"):
#        with open("out.txt", "r") as file:
#            line = file.readline()
#            return [int(x) for x in line.split()]
        
    def step(self, verbose = True):
        """
        n : quantité de fois que chaque joueur joue chaque arène.
        nbArenas : quantité d'arènes (numerotées de 0 à nbArenas-1).
        """
        for joueur in range(self.nbPopulation):
            for arena in range(self.nbArenas):
                for enemi in range(self.en):
                    for fois in range(self.n):
                        if verbose:
                            print("Joueur {}, arène {}, enemi {}, fois {}".format(joueur, arena, enemi, fois))
                        self.jeu.reset(arena, self.w[joueur, :], enemi)
                        self.jeu.run()
                        res = self.jeu.computeOccupancyGrid()
                        if verbose:
                            print(res)
                        self.results[joueur] += (res[0] > res[1])

    def mutationSimple(self, wRow):
        newWRow = wRow.copy()
        wRowRand = self.wRowRandom()
        for i in range(2*self.nbFeatures):
            if np.random.rand() < self.mutation:
                newWRow[i] = wRowRand[i]
        return newWRow
    
    def mutationDouble(self, wRow1, wRow2):
        newWRow = np.empty(2*self.nbFeatures)
        for i in range(2*self.nbFeatures):
            if np.random.rand() < 0.5:
                newWRow[i] = wRow1[i]
            else:
                newWRow[i] = wRow2[i]
        return self.mutationSimple(newWRow)
    
    def wRowRandom(self):
        w = np.empty(2*self.nbFeatures)
        w[0] = np.random.randint(2, 10)*10
        w[1] = np.random.randint(0, 13)*10
        w[2:10] = np.random.choice(np.arange(-1, 1.1, 0.1), size=8)
        w[10] = np.random.choice(np.arange(0, 1.1, 0.1))
        w[11:19] = np.random.choice(np.arange(-1, 1.1, 0.1), size=8)
        w[19] = np.random.choice(np.arange(0.5, 1.1, 0.1))
        w[20] = np.random.choice(np.arange(0, 1.1, 0.1))
        w[21] = np.random.choice(np.arange(-1, 1.1, 0.1))
        w[22] = np.random.randint(2, 10)*10
        w[23] = np.random.randint(0, 13)*10
        w[24:32] = np.random.choice(np.arange(-1, 1.1, 0.1), size=8)
        w[32] = np.random.choice(np.arange(0, 1.1, 0.1))
        w[33:41] = np.random.choice(np.arange(-1, 1.1, 0.1), size=8)
        w[41] = np.random.choice(np.arange(0.5, 1.1, 0.1))
        w[42] = np.random.choice(np.arange(0, 1.1, 0.1))
        w[43] = np.random.choice(np.arange(-1, 1.1, 0.1))
        return w

    def evolve(self):
        newW = np.zeros(self.w.shape)
        classification = np.argsort(-self.results)
        for i in range(self.nbGood):
            j = classification[i]
            newW[i, :] = self.mutationSimple(self.w[j, :])
        for i in range(self.nbBad):
            j = classification[-i-1]
            newW[self.nbGood + i, :] = self.mutationSimple(self.w[j, :])
        for i in range(self.nbGood+self.nbBad, self.nbPopulation - self.nbRandom):
            parent1 = 0
            parent2 = 0
            while parent1==parent2:
                parent1 = np.random.randint(0, self.nbGood+self.nbBad)
                parent2 = np.random.randint(0, self.nbGood+self.nbBad)
            newW[i, :] = self.mutationDouble(self.w[parent1, :], self.w[parent2, :])
        for i in range(self.nbPopulation - self.nbRandom, self.nbPopulation):
            newW[i, :] = self.wRowRandom()
        self.w = newW
        self.results = np.zeros(self.nbPopulation, dtype=int)
        
    def run(self, nRun, verbose = True):
        for i in range(nRun):
            if not (self.fromFile and i==0):
                self.step(verbose)
                if verbose:
                    print("Itération",i,":")
                    for j in range(self.nbPopulation):
                        print("Joueur {}: {}".format(j, self.results[j]))
                self.save("result{}.npz".format(i))
            self.evolve()
        
if __name__=="__main__":
    ag = AlgoGenetique(nbPopulation = 20, nbFeatures = 22, mutation = 1/22,\
                       pGood = 0.40, pBad = 0.1, pRandom = 0.0,\
                       n = 3, nbArenas = 4, en = 3)
    for i in range(3):
        ag.w[i, :] = np.array([60,
                               90,
                               0., 0.2, 0.5, 0.7, -0.8, -0.6, -0.3, 0.,
                               1,
                               0., -0.9, -0.6, -0.7, 0.7, 0.6, 0.9, 0.,
                               0.8,
                               1,
                               0,
                               60,
                               90,
                               0., 0.2, 0.5, 0.7, -0.8, -0.6, -0.3, 0.,
                               1,
                               0., -0.9, -0.6, -0.7, 0.7, 0.6, 0.9, 0.,
                               0.8,
                               1,
                               0])
    for i in range(3):
        ag.w[i + 2, :] = np.array([ 8.00000000e+01,  1.10000000e+02, -5.00000000e-01,  4.00000000e-01,
        7.00000000e-01,  7.00000000e-01,  8.00000000e-01,  5.00000000e-01,
       -3.00000000e-01, -6.00000000e-01,  0.00000000e+00, -8.00000000e-01,
        3.00000000e-01,  1.00000000e-01, -7.00000000e-01, -1.00000000e+00,
       -2.00000000e-01,  1.00000000e+00, -9.00000000e-01,  8.00000000e-01,
        1.00000000e-01, -2.00000000e-01,  3.00000000e+01,  1.10000000e+02,
        1.00000000e+00,  2.00000000e-01,  6.00000000e-01, -2.22044605e-16,
       -7.00000000e-01, -2.00000000e-01, -9.00000000e-01,  0.00000000e+00,
        6.00000000e-01,  5.00000000e-01,  4.00000000e-01, -6.00000000e-01,
       -7.00000000e-01, -3.00000000e-01, -1.00000000e+00,  9.00000000e-01,
       -7.00000000e-01,  5.00000000e-01,  0.00000000e+00, -8.00000000e-01])
    
    ag.w[6, :] = np.array([ 6.00000000e+01,  9.00000000e+01,  3.00000000e-01,  2.00000000e-01,   
    5.00000000e-01,  7.00000000e-01,  8.00000000e-01, -5.00000000e-01,
   -3.00000000e-01,  0.00000000e+00,  1.00000000e+00,  0.00000000e+00,
   -9.00000000e-01, -6.00000000e-01, -7.00000000e-01, -1.00000000e+00,
   -2.00000000e-01,  9.00000000e-01,  5.00000000e-01,  8.00000000e-01,
    1.00000000e+00,  0.00000000e+00,  6.00000000e+01,  9.00000000e+01,
   -2.22044605e-16,  2.00000000e-01,  5.00000000e-01,  7.00000000e-01,
   -8.00000000e-01, -6.00000000e-01, -3.00000000e-01,  0.00000000e+00,
    1.00000000e+00,  4.00000000e-01, -1.00000000e-01,  6.00000000e-01,
   -7.00000000e-01,  1.00000000e-01,  6.00000000e-01,  9.00000000e-01,
    0.00000000e+00,  8.00000000e-01,  1.00000000e+00, -1.00000000e+00])
    
    
    
    ag.run(6)