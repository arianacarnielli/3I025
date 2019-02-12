# -*- coding: utf-8 -*-

import random
import time as t
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st
#import os

def creerListePref(nomFichierEtu, nomFichierSpe):
    """
        Prend en argument le nom de deux fichiers. Le premier est cense d'etre
        un fichier du type TestPrefEtu et le deuxieme un fichier du type TestPrefSpe.
        Retourne deux matrices.
        La premiere matrice represente la liste de preferences des etudiants.
        Chaque ligne commence par l'identifiant de l'etudiant et apres sa liste
        de preferences (ligne[2][3] est donc l'identifiant du master en 3eme place
        pour l'etudiant 2).
        La deuxieme matrice represente la liste de preferences des masters.
        La premiere ligne contient les capacites d'accueil des parcours.
        Ensuite chaque ligne commence par l'identifiant du master et apres sa liste
        de preference pour les estudiants (ligne[4][5] est donc l'identifiant de
        l'etudiant en 5eme place pour le master 3).
    """

    monFichierEtu = open(nomFichierEtu, "r")
    contenuEtu = monFichierEtu.readlines()

    monFichierSpe = open(nomFichierSpe, "r")
    contenuSpe = monFichierSpe.readlines()

    monFichierEtu.close()
    monFichierSpe.close()

    for i in range(1, len(contenuEtu)):
        contenuEtu[i] = contenuEtu[i].split()
        del contenuEtu[i][1]
        contenuEtu[i] = list(map(int, contenuEtu[i]))

    del contenuEtu[0]

    for i in range(2, len(contenuSpe)):
        contenuSpe[i] = contenuSpe[i].split()
        del contenuSpe[i][1]
        contenuSpe[i] = list(map(int, contenuSpe[i]))

    del contenuSpe[0]
    contenuSpe[0] = contenuSpe[0].split()
    del contenuSpe[0][0]
    contenuSpe[0] = list(map(int, contenuSpe[0]))

    ##afficherTab(contenuEtu)
    ##print("\n")
    ##afficherTab(contenuSpe)
    ##print("\n")
    return contenuEtu, contenuSpe


def afficherTab(tab):
    """
    """
    for line in tab:
        print(line)

def afficherDico(dic):
    """
    """
    for key in dic:
        print(key, ":", dic[key])
    print("\n")


def algoGS(nomFichierEtu, nomFichierSpe):
    """

    """
    #creer les matrices de preferences
    ListeEtu, ListeMaster = creerListePref(nomFichierEtu, nomFichierSpe)
    #initialiser chaque etudiant comme libre
    ListeEtuLibre = ListeEtu.copy()
    #On retire la ligne avec les capacites de la matrice des masters pour faciliter les references
    ListeCapacite = ListeMaster.pop(0)

    #On cree un dictionnaire d'index. Chaque entree a comme cle l'identifiant d'un etudiant
    #et comme valeur l'index du prochain master a etre teste. Initialise avec la valeur 1 pour
    #tout les cles car 1 est l'index du debut de la liste.
    DicoIndexMaster = {}
    for etu in ListeEtu:
        DicoIndexMaster[etu[0]] = 1

    #On cree un dictionnaire des couples stables. Chaque entree a comme cle l'identifiant
    #d'un master et comme valeur une liste des etudiants inscris (liste car on peut avoir
    #plus d'un etudiant pour un master donne). Initialise avec des listes vides.
    DicoCouples = {}
    for master in ListeMaster:
        DicoCouples[master[0]] = []

    #Tant qu'il existe un etudiant libre, on prend un etudiant
    while len(ListeEtuLibre) > 0:

        etu = ListeEtuLibre.pop(0)
        #On prend l'index de son tableau de preferences pour voir quel est le prochaine master a essayer
        indexMaster = DicoIndexMaster[etu[0]]

        #Pour chacun des master pas encore testes pour cet etudiant, on essaye de l'inscrire
        for iM in range (indexMaster, len(ListeMaster) + 1):
            #master = l'identifiant du master qu'on essaie maintenant
            master = etu[iM]
            #S'il y a de la place dans ce master
            if (len(DicoCouples[master]) < ListeCapacite[master]):
                #On inscrit l'etudiant au master. Ajouter etu à DicoCouples[master]
                DicoCouples[master].append(etu[0])
                #Mis a jour de l'index du tableau de preferences de l'etudiant
                DicoIndexMaster[etu[0]] += 1
                #On passe au prochain etudiant libre
                break

            #Si on arrive ici, c'est qu'il n'y a pas de place au master
            #On teste pour voir s'il faut remplacer un etudiant deja inscrit
            #maxEtu = identifiant de l'etudiant le moins prioritaire, au debut l'identifiant de etu
            maxEtu = etu[0]
            #On teste chaque etudiant deja inscrit
            for y in DicoCouples[master]:
                #Si un etudiant deja rempli est moins prioritaire que maxEtu, on actualise maxEtu
                if (ListeMaster[master].index(y, 1) > ListeMaster[master].index(maxEtu, 1)):
                    maxEtu = y
            #Si different, alors il faut liberer un etudiant et inscrire etu
            if (maxEtu !=etu[0]):
                #On inscrit etu au master
                DicoCouples[master].append(etu[0])
                #Mis a jour de l'index du tableau de preferences de l'etudiant
                DicoIndexMaster[etu[0]] += 1
                #On retire l'etudiant avec la pire priorite
                DicoCouples[master].remove(maxEtu)
                #On reajoute cet etudiant a la liste des etudiants libres
                ListeEtuLibre.append(ListeEtu[maxEtu])
                #On passe au prochain etudiant libre
                break

            #L'etudiant n'arrive pas a s'inscrire a ce master, on essaie le master suivant
            #Mis a jour de l'index du tableau de preferences de l'etudiant
            DicoIndexMaster[etu[0]] += 1

    return DicoCouples


#r = creerListePref("TestPrefEtu.txt", "TestPrefSpe.txt")
#afficherTab(r[0])
#print("\n")
#afficherTab(r[1])
#print("\n")

#gs = algoGS("TestPrefEtu.txt", "TestPrefSpe.txt")
#print(gs)

###############################################################################
#Je essaie de generaliser un peut la fonction qui applique l'algorithme
#Pour ça, je fais un pre-traitement des matrices pour avoir la bonne forme
###############################################################################

def algoGSEtu(nomFichierEtu, nomFichierSpe):
    """
    Algorithme Gale-Shapley applique coté etudiant.
    Prend en argument le nom de deux fichiers. Le premier est cense d'etre
    un fichier du type TestPrefEtu et le deuxieme un fichier du type TestPrefSpe.
    Retourne le resultat de la fonction AlgoGS2 sur les deux matrices crees par
    creerListePref a partir des fichiers.
    Le resultat est un dictionaire ou les cles sont les identifiants des masters
    et les valeurs des listes des identifiants des etudiants.
    """
    ListeEtu, ListeMaster = creerListePref(nomFichierEtu, nomFichierSpe)

    return algoGS2(ListeEtu, ListeMaster)

def algoGSSpe(nomFichierSpe, nomFichierEtu):
    """
    Algorithme Gale-Shapley applique coté masters.
    Prend en argument le nom de deux fichiers. Le premier est cense d'etre
    un fichier du type TestPrefSpe et le deuxieme un fichier du type TestPrefEtu.
    Fait un traitement sur les deux matrices crees par creerListePref a partir
    des fichiers, pour les rendre aux format pris par AlgoGS2.
    Le resultat est un dictionaire ou les cles sont les identifiants des masters
    et les valeurs des listes des identifiants des etudiants.

    """
    ListeEtu, ListeMaster = creerListePref(nomFichierEtu, nomFichierSpe)
    #ListeMaster ne doit plus avoir la ligne avec les capacites
    ListeCapaciteMaster = ListeMaster.pop(0)
    #ListeEtu doit avoir une ligne au debut avec les capacites, toujours 1
    ListeCapaciteEtu = [1 for i in range(len(ListeEtu))]
    ListeEtu.insert(0, ListeCapaciteEtu)

    #A chaque fois qu'un element de ListeMaster a une capacite plus grand que 1, il faut
    #mettre des lignes en plus dans la matrice pour signaler cela
    ListeMasterRe = []
    for i in range(0, len(ListeMaster)):
        quant = ListeCapaciteMaster[i]
        while quant > 1:
            ListeMasterRe.insert(i, ListeMaster[i])
            quant-=1
    ListeMaster.extend(ListeMasterRe)

    #Le resultat rendu par algoGS2 est un ditionnaire ou les cles sont les identifiants
    #des etudiants. Il faut les inverser pour avoir un resultat avec la meme ordre
    #que l'autre application ded l'algo. Comme cela la fonction de teste de couples instables
    #peut etre la meme
    Dico = algoGS2(ListeMaster, ListeEtu)
    DicoRes = {}
    for x in Dico:
        for y in Dico[x]:
            if y in DicoRes:
                DicoRes[y].append(x)
            else:
                DicoRes[y] = [x]
    return DicoRes
#    return Dico

def algoGS2(ListeCote, ListeAutre):
    """
    Application plus generaliste de l'algorithme Gale-Shapley.
    Prend 2 matrices en argument, senses d'etre des matrices de preferences.
    La 2eme matrice doit avoir une ligne au debut qui signale les capacites de ces elements.
    La fonction applique l'algorithme coté la premiere matrice passe en argument.
    """
    #initialiser chaque element de ListeCote comme libre
    ListeCoteLibre = ListeCote.copy()
    #On recupere la ligne avec les capacites de la matrice ListeAutre
    ListeCapacite = ListeAutre.pop(0)

    #On cree un dictionnaire d'index. Chaque entree a comme cle l'identifiant d'un element
    #de ListeCote et comme valeur l'index du prochain element de ListeAutre a etre teste.
    #Initialise avec la valeur 1 pour tout les cles car 1 est l'index du debut de la liste.
    DicoIndexAutre = {}
    for elem in ListeCote:
        DicoIndexAutre[elem[0]] = 1

    #On cree un dictionnaire des couples stables. Chaque entree a comme cle l'identifiant
    #d'un elemente de ListeAutre et comme valeur une liste des elements de ListeCote
    #(liste car on peut avoir plus d'un element pour une cle donne).
    #Initialise avec des listes vides.
    DicoCouples = {}
    for autre in ListeAutre:
        DicoCouples[autre[0]] = []

    #Tant qu'il existe un element libre, on prend un element
    while len(ListeCoteLibre) > 0:

        elem = ListeCoteLibre.pop(0)
        #On prend l'index de son tableau de preferences pour voir quel est le prochaine element de ListeAutre a essayer
        indexAutre = DicoIndexAutre[elem[0]]

        #Pour chacun des elements de ListeAutre pas encore testes pour elem, on essaye
        for iM in range (indexAutre, len(ListeAutre) + 1):
            #id_autre = l'identifiant de l'element de ListeAutre qu'on essaie maintenant
            id_autre = elem[iM]
            #S'il y a de la place


            if (len(DicoCouples[id_autre]) < ListeCapacite[id_autre]):

                #On cree un couple. Ajouter elem à DicoCouples[id_autre]
                DicoCouples[id_autre].append(elem[0])
                #Mis a jour de l'index du tableau de preferences de elem
                DicoIndexAutre[elem[0]] += 1
                #On passe au prochain element libre
                break

            #Si on arrive ici, c'est qu'il n'y a pas de place au element de ListeAutre
            #On teste pour voir s'il faut remplacer un element deja en couple
            #maxElem = identifiant de l'element le moins prioritaire, au debut l'identifiant de elem
            maxElem = elem[0]
            #On teste chaque element deja en couple
            for y in DicoCouples[id_autre]:
                #Si un element deja rempli est moins prioritaire que maxElem, on actualise maxElem
                if (ListeAutre[id_autre].index(y, 1) > ListeAutre[id_autre].index(maxElem, 1)):
                    maxElem = y
            #Si different, alors il faut liberer un element et coupler elem
            if (maxElem !=elem[0]):
                #On couple elem
                DicoCouples[id_autre].append(elem[0])
                #Mis a jour de l'index du tableau de preferences de l'elem
                DicoIndexAutre[elem[0]] += 1
                #On retire l'element avec la pire priorite
                DicoCouples[id_autre].remove(maxElem)
                #On reajoute cet element a la liste des elements libres
                ListeCoteLibre.append(ListeCote[maxElem])
                #On passe au prochain element libre
                break

            #elem n'arrive pas a faire un couple, on essaie l'element de ListeAutre suivant
            #Mis a jour de l'index du tableau de preferences de elem
            DicoIndexAutre[elem[0]] += 1

    return DicoCouples


def testCouplesInstables(DicoCouples, ListeEtu, ListeMaster):
    """

    """
    #On enleve la ligne avec les capacites des masters
    ListeMaster.pop(0)
    #Dictionnaire des couples instlabes trouves
    DicoInst = {}
    #Pour chaque couple dans DicoCouples
    for master in DicoCouples:
        #Pour un etudiant dans un couple
        for etu in DicoCouples[master]:
            #On regarde quels sont les masters que l'etudiant en question prefererait
            #au master ou il est inscrit
            listePref = ListeEtu[etu].copy()
            listePref.pop(0)
            i = 0
            while listePref[i] != master:
                i+= 1
            del listePref [i:]
            #On regarde dans ces masters, quel sont les etudiants inscrits
            for masterPref in listePref:
                listeIns = DicoCouples[masterPref].copy()
                #Pour chaque etudiant inscrit dans ce master, on regarde si sa priorite
                #est plus baisse que celle de etu
                for autreEtu in listeIns:
                    #Si oui, alors couple instable
                    if(ListeMaster[masterPref].index(autreEtu, 1) > ListeMaster[masterPref].index(etu,1)):
                        if masterPref in DicoInst:
                            DicoInst[masterPref].append(etu)
                        else:
                            DicoInst[masterPref] = [etu]
    return DicoInst


def genEtu(n):
    """
    """
    res = []
    c = list(range(0, 9))
    for i in range(n):
        res.append(random.sample(c, 9))
        res[i].insert(0, i)
    return res

def genMaster(n):
    """
    """
    res = []
    c = list(range(0, n))
    for i in range(9):
        res.append(random.sample(c, n))
        res[i].insert(0, i)

    cap = n//9
    c = [cap]*9
    manque = n - (cap * 9)
    for i in range(manque):
        c[i%n]+=1

    res.insert(0, c)
    return res

def algoGSEtu2(ListeEtu, ListeMaster):
    """
    Algorithme Gale-Shapley applique coté etudiant.
    Prend en argument deux matrices. La premiere est cense d'etre du type TestPrefEtu
    et le deuxieme du type TestPrefSpe.
    Retourne le resultat de la fonction AlgoGS2 sur les deux matrices.
    Le resultat est un dictionaire ou les cles sont les identifiants des masters
    et les valeurs des listes des identifiants des etudiants.
    """
    return algoGS2(ListeEtu, ListeMaster)

def algoGSSpe2(ListeEtu, ListeMaster):
    """
    Algorithme Gale-Shapley applique coté masters.
    Prend en argument le nom de deux matrices. Le premier est cense d'etre
    une matrice du type TestPrefEtu et le deuxieme du type TestPrefSpe.
    Fait un traitement sur les deux matrices pour les rendre aux format pris par AlgoGS2.
    Le resultat est un dictionaire ou les cles sont les identifiants des masters
    et les valeurs des listes des identifiants des etudiants.

    """
    #ListeMaster ne doit plus avoir la ligne avec les capacites
    ListeCapaciteMaster = ListeMaster.pop(0)
    #ListeEtu doit avoir une ligne au debut avec les capacites, toujours 1
    ListeCapaciteEtu = [1 for i in range(len(ListeEtu))]
    ListeEtu.insert(0, ListeCapaciteEtu)

    #A chaque fois qu'un element de ListeMaster a une capacite plus grand que 1, il faut
    #mettre des lignes en plus dans la matrice pour signaler cela
    ListeMasterRe = []
    for i in range(0, len(ListeMaster)):
        quant = ListeCapaciteMaster[i]
        while quant > 1:
            ListeMasterRe.insert(i, ListeMaster[i])
            quant-=1
    ListeMaster.extend(ListeMasterRe)

    #Le resultat rendu par algoGS2 est un ditionnaire ou les cles sont les identifiants
    #des etudiants. Il faut les inverser pour avoir un resultat avec la meme ordre
    #que l'autre application ded l'algo. Comme cela la fonction de teste de couples instables
    #peut etre la meme
    Dico = algoGS2(ListeMaster, ListeEtu)
    DicoRes = {}
    for x in Dico:
        for y in Dico[x]:
            if y in DicoRes:
                DicoRes[y].append(x)
            else:
                DicoRes[y] = [x]
    return DicoRes
#   return Dico

def tempsExec(n, func):
    """
    """
    start = t.process_time()
    for fois in range(10):
        ListeMaster = genMaster(n)
        ListeEtu = genEtu(n)
        func(ListeEtu, ListeMaster)
    return (t.process_time() - start)/10

def testFichier(nomFichier, func):
    """
    """
    with open(nomFichier, "w") as file:
        for n in range(200, 20000, 100):
            duree = tempsExec(n, func)
            file.write("{} {}\n".format(n, duree))
            file.flush()
            print(n, duree)
            if duree > 60:
                break

def creerGraphe(nomFichier, nom):
    """
    """
    plt.close(1)
    plt.figure(1)
    plt.grid(True)
    plt.xlabel("log(n)")
    plt.ylabel("log(temps) (en secondes)")
    plt.title(nom)
    n = []
    temps = []

    with open(nomFichier, "r") as file:
        for line in file:
            L = line.split()
            n.append(int(L[0]))
            temps.append(float(L[1]))
    n = np.log(n)
    temps = np.log(temps)
    plt.plot(n, temps, label= "valeurs expérimentales", zorder = 2)

    slope, intercept, _, _, _ = st.linregress(n, temps)
    plt.plot([n[0], n[-1]], [slope*n[0] + intercept, slope*n[-1] + intercept], label=  "droite de regression linéaire\na = {:.3f}".format(slope), zorder = 1)

    plt.legend(loc = "upper left")


def calcUtilite(ListeEtu, k):
    """
    Retourne un dictionnaire ou les cles vont de 1 a k et les valeurs sont
    des listes de couples (etu, mast), ou etu est l'identifiant d'un etudiant
    et mast l'identifiant d'un master. La valeur a la cle i sont tous les couples
    (etu, masts) avec utilite i.

    """
    dico = {}

    for i in range(1, k+1):
        dico[i] = []

    for etu in ListeEtu:
        for i in range(1, k+1):
            dico[i].append((etu[0], etu[i]))

    return dico

def creerPLUtilMax(nomFichier, ListeEtu, ListeMaster):
    """
    """
    with open(nomFichier, "w") as file:
        file.write("Maximize\n")
        file.write("obj: ")
        taille = len(ListeEtu[0]) - 1
        var = calcUtilite(ListeEtu, taille)
        s = ""
 
        for util in var:
            s +=  " + ".join([str(taille - util)+" x"+str(k)+str(v) for k,v in var[util] ])
            s += " + "
        s = s[:-3]
        file.write(s)
        file.write("\n")

        file.write("Subject To\n")
        cont = 1
        for i in range(len(ListeEtu)):
            s = ""
            s += "c"+ str(cont) + ": "
            for util in var:
                s += "x" + str(var[util][i][0])+str(var[util][i][1])
                s += " + "
            cont+=1
            s = s[:-3]
            s += " = 1"
            file.write(s)
            file.write("\n")

        ListeCapaciteMaster = ListeMaster.pop(0)
        for i in range(len(ListeMaster)):
            s = ""
            s += "c"+ str(cont) + ": "
            for l in var.values():
                for u,v in l:
                    if v == i:
                        s += "x" + str(u) + str(v)
                        s += " + "
            if len(s) > 5:
                s = s[:-3]
                s += " = "+ str(ListeCapaciteMaster[i])
                file.write(s)
                file.write("\n")
                cont+=1
        file.write("Binary \n")
        s = ""
        for util in var:
            s +=  " ".join(["x"+str(k)+str(v) for k,v in var[util] ])
            s += " "
        file.write(s)
        file.write("\n")
        file.write("End")


def creerPLUtilMoyen(nomFichier, ListeEtu, ListeMaster, k):
    """
    """
    with open(nomFichier, "w") as file:
        file.write("Maximize\n")
        file.write("obj: ")
        var = calcUtilite(ListeEtu, k)
        s = ""
        for util in var:
            s +=  " + ".join(["x"+str(k)+str(v) for k,v in var[util] ])
            s += " + "
        s = s[:-3]
        file.write(s)
        file.write("\n")

        file.write("Subject To\n")
        cont = 1
        for i in range(len(ListeEtu)):
            s = ""
            s += "c"+ str(cont) + ": "
            for util in var:
                s += "x" + str(var[util][i][0])+str(var[util][i][1])
                s += " + "
            cont+=1
            s = s[:-3]
            s += " <= 1"
            file.write(s)
            file.write("\n")

        ListeCapaciteMaster = ListeMaster.pop(0)
        for i in range(len(ListeMaster)):
            s = ""
            s += "c"+ str(cont) + ": "
            for l in var.values():
                for u,v in l:
                    if v == i:
                        s += "x" + str(u) + str(v)
                        s += " + "
            if len(s) > 5:
                s = s[:-3]
                s += " <= "+ str(ListeCapaciteMaster[i])
                file.write(s)
                file.write("\n")
                cont+=1
        file.write("Binary \n")
        s = ""
        for util in var:
            s +=  " ".join(["x"+str(k)+str(v) for k,v in var[util] ])
            s += " "
        file.write(s)
        file.write("\n")
        file.write("End")









if __name__ == "__main__":


    ListeEtu, ListeMaster = creerListePref("PrefEtu.txt", "PrefSpe.txt")
    afficherDico(calcUtilite(ListeEtu, len(ListeEtu[0]) -1))
    creerPLUtilMax("test_max.lp", ListeEtu, ListeMaster)
    #creerPLUtilMoyen("pl_2.lp", ListeEtu, ListeMaster, 2)
    #os.system('export GUROBI_HOME="/opt/gurobi801/linux64"')
    #os.system('export PATH="${PATH}:${GUROBI_HOME}/bin"')
    #os.system('export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"')
    #os.system("/opt/gurobi801/linux64/bin/gurobi_cl ResultFile=sol2.sol pl_2.lp")
    #afficherTab(ListeEtu)

    #afficherTab(ListeEtu)
    #print("\n")
    #afficherTab(ListeMaster)
    #print("\n")
    #dico = calcUtilite(ListeEtu, 3)
    #afficherDico(dico)
    #print("\n")
    #teste = ""
    #for i in dico:
    #    teste = " + ".join(["x"+str(k)+str(v) for k,v in dico[i] ])
    #
    #print(teste)

    #testFichier("test_master.txt", algoGSSpe2)
    #creerGraphe("test_master.txt", "Côté Master")




    #ListeMaster = genMaster(200)
    #ListeEtu = genEtu(200)

    #afficherDico(algoGSEtu2(ListeEtu, ListeMaster))


    #ListeEtu, ListeMaster = creerListePref("TestPrefEtu.txt", "TestPrefSpe.txt")
    #DicoCouples1 = algoGSEtu("TestPrefEtu.txt", "TestPrefSpe.txt")
    #print(DicoCouples1)
    #print ("\n")
    #
    #ListeEtu, ListeMaster = creerListePref("TestPrefEtu.txt", "TestPrefSpe.txt")
    #DicoCouples2 = algoGSSpe("TestPrefSpe.txt", "TestPrefEtu.txt")
    #print(DicoCouples2)
    #print ("\n")
    #
    #ListeEtu, ListeMaster = creerListePref("TestPrefEtu.txt", "TestPrefSpe.txt")
    #print(testCouplesInstables(DicoCouples2, ListeEtu, ListeMaster))
    #print ("\n")
    #
    #ListeEtu, ListeMaster = creerListePref("TestPrefEtu.txt", "TestPrefSpe.txt")
    #print(testCouplesInstables(DicoCouples1, ListeEtu, ListeMaster))
    #print ("\n")
    #
    #DicoCouples = {0:[5,3],
    #               1:[4],
    #               2:[2],
    #               3:[9],
    #               4:[10],
    #               5:[1],
    #               6:[6],
    #               7:[7],
    #               8:[8,0]
    #               }
    #print(DicoCouples)
    #print("\n")
    #
    #ListeEtu, ListeMaster = creerListePref("TestPrefEtu.txt", "TestPrefSpe.txt")
    #print(testCouplesInstables(DicoCouples, ListeEtu, ListeMaster))
    #print ("\nteste avec des donnees du tme 2\n\n")

    #ListeEtu, ListeMaster = creerListePref("PrefEtu.txt", "PrefSpe.txt")
    #afficherTab(ListeMaster)
    #print("\n")
    #afficherTab(ListeEtu)
    #DicoCouples1 = algoGSEtu("PrefEtu.txt", "PrefSpe.txt")
    #print(DicoCouples1)
    #"print ("\n")
    #afficherDico(DicoCouples1)

    #ListeEtu, ListeMaster = creerListePref("PrefEtu.txt", "PrefSpe.txt")
    #afficherTab(ListeMaster)
    #print("\n")
    #afficherTab(ListeEtu)

    #DicoCouples1 = algoGSEtu("PrefEtu.txt", "PrefSpe.txt")
    #print ("\n")
    #afficherDico(DicoCouples1)

    #ListeEtu, ListeMaster = creerListePref("PrefEtu.txt", "PrefSpe.txt")
    #print(testCouplesInstables(DicoCouples1, ListeEtu, ListeMaster))

