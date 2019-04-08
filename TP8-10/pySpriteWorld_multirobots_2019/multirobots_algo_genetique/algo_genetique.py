# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 20:03:33 2019

@author: arian
"""

import numpy as np
import os

class AlgoGenetique:
    def __init__(self, nbPopulation, nbFeatures, mutation,\
                 pGood, pBad, pRandom,\
                 n, nbArenas, filename = None):
        self.wValues = np.array([-1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1])
        self.fromFile = False
        if filename is not None:
            self.fromFile = True
            with np.load(filename) as file:
                self.w = file["w"]
                self.mutation = file["mutation"][0]
                self.nbPopulation, self.nbFeatures = self.w.shape
                self.results = file["results"]
        else:
            self.nbPopulation = nbPopulation
            self.mutation = mutation
            self.nbFeatures = nbFeatures
            self.w = np.random.choice(self.wValues, size=(self.nbPopulation, self.nbFeatures))
            self.results = np.zeros(self.nbPopulation, dtype=int)
        self.nbGood = int(pGood*self.nbPopulation)
        self.nbBad = int(pBad*self.nbPopulation)
        self.nbRandom = int(pRandom*self.nbPopulation)
        assert self.nbGood > 0 and self.nbGood+self.nbBad+self.nbRandom < self.nbPopulation
        self.n = n
        self.nbArenas = nbArenas
        
    def save(self, filename):
        np.savez(filename, w = self.w, mutation = np.array([self.mutation]), results = self.results)

    def sendWToSimul(wRow, arena, filename = "in.txt"):
        with open(filename, "w") as file:
            file.write("{:d}\n".format(arena))
            string = " ".join(["{:.1f}".format(e) for e in wRow])
            file.write(string)
    
    def getResultFromSimul(filename = "out.txt"):
        with open("out.txt", "r") as file:
            line = file.readline()
            return [int(x) for x in line.split()]
        
    def step(self, verbose = True):
        """
        n : quantité de fois que chaque joueur joue chaque arène.
        nbArenas : quantité d'arènes (numerotées de 0 à nbArenas-1).
        """
        for joueur in range(self.nbPopulation):
            for arena in range(self.nbArenas):
                for fois in range(self.n):
                    if verbose:
                        print("Joueur {}, arène {}, fois {}".format(joueur, arena, fois))
                    AlgoGenetique.sendWToSimul(self.w[joueur, :], arena)
                    os.system("python -m multirobots_algo_genetique.py")
                    res = AlgoGenetique.getResultFromSimul()
                    self.results[joueur] += (res[0] > res[1])

    def mutationSimple(self, wRow):
        newWRow = wRow.copy()
        for i in range(self.nbFeatures):
            if np.random.rand() < self.mutation:
                newWRow[i] = np.random.choice(self.wValues)
        return newWRow
    
    def mutationDouble(self, wRow1, wRow2):
        newWRow = np.empty(self.nbFeatures)
        for i in range(self.nbFeatures):
            if np.random.rand() < 0.5:
                newWRow[i] = wRow1[i]
            else:
                newWRow[i] = wRow2[i]
        return self.mutationSimple(newWRow)
    
    def wRowRandom(self):
        return np.random.choice(self.wValues, size=self.nbFeatures)

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
    ag = AlgoGenetique(nbPopulation = 20, nbFeatures = 25, mutation = 1/25,\
                       pGood = 0.25, pBad = 0.1, pRandom = 0.0,\
                       n = 5, nbArenas = 3)
    for i in range(4):
        ag.w[i, :] = np.array([0, 1, 1, 1, -1, -1, -1, 0,\
                               0, 1, 1, 1, -1, -1, -1, 0,\
                               0, 1, 1, 1, -1, -1, -1, 0,\
                               0])
    ag.run(6)