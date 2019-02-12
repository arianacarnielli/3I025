# -*- coding: utf-8 -*-

def afficherListe(l):
    for e in l:
        print(e)


def afficherDico(d):
    for k in d:
        print(k, ":", d[k])
    print("\n")


""" retourne le classement de idEtu pour idMaster dans matSpe
"""
def getEtuRank(idEtu, idMaster, matSpe):
    return (matSpe[idMaster][1::]).index(idEtu)


""" insère idEtu dans la list l par ordre croissant de préférence,
    ordre défini par matSpe pour idMaster
"""
def insertEtuDecr(l, idEtu, idMaster, matSpe):
    for i in range(len(l)):
        if ( getEtuRank(idEtu,idMaster,matSpe)<getEtuRank(l[i],idMaster,matSpe) ):
            l.insert(i, idEtu)
            return
    l.append(idEtu)     # insertion en fin de liste sinon


def creerListePref (nomFichierEtu, nomFichierSpe):
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

    return contenuEtu, contenuSpe


def algoGS(matEtu, matSpe):

    # listeEtuLibres := [idEtu_0, idEtu_1, ..., idEtu_n-1] 
    listeEtuLibres = []
    for ligneEtu in matEtu:
        listeEtuLibres.append(ligneEtu[0])

    # listeMasters := [idMaster_0, idMaster_1, ..., idMaster_n-1]
    listeMasters = []
    for ligneSpe in matSpe:
        listeMasters.append(ligneSpe[0])
    del listeMasters[0]
    
    # dicoCapaMaster := { idMaster : capacité }
    dicoCapaMaster = {}
    for master in listeMasters:
        dicoCapaMaster[master] = matSpe[0][master]
    del matSpe[0]

    # dicoIndexNextMaster := { idEtu : indice_prochain_master_à_tester}
    dicoIndexNextMaster = {}
    for idEtu in listeEtuLibres:
        dicoIndexNextMaster[idEtu] = 1

    # dicoCouples := { idMaster : [idEtu_0, idEtu_1, ...] }
    dicoCouples = {}
    for idMaster in listeMasters:
        dicoCouples[idMaster] = []

    while (len(listeEtuLibres)>0):
        print(listeEtuLibres)       # debug
        afficherDico(dicoCouples)   # debug
        idEtu = listeEtuLibres[0]
        indexNextMaster = dicoIndexNextMaster[idEtu]
        for indexMaster in range (indexNextMaster, len(matEtu[idEtu]) -1):
            # si pas complet
            idMaster = matEtu[idEtu][indexMaster]
            if ( len(dicoCouples[idMaster]) < dicoCapaMaster[idMaster] ):
                insertEtuDecr(dicoCouples[idMaster], idEtu, idMaster, matSpe)
                listeEtuLibres.remove(idEtu)
                dicoIndexNextMaster[idEtu] = indexMaster+1;
                break
            # sinon si etu est preferable à min(dicoCouples[master])
            # plus le rang est petit, plus il est bon
            elif ( getEtuRank(idEtu,idMaster,matSpe)<getEtuRank(dicoCouples[idMaster][-1],idMaster,matSpe) ):
                # virer min(dicoCouples[idMaster])
                listeEtuLibres.append(dicoCouples[idMaster][-1])
                del dicoCouples[idMaster][-1]
                # ajouter idEtu à dicoCouples[idMaster]
                insertEtuDecr(dicoCouples[idMaster], idEtu, idMaster, matSpe)
                listeEtuLibres.remove(idEtu)
                dicoIndexNextMaster[idEtu] = indexMaster+1;
                break
            # sinon
                # rejet (on continu)

    return dicoCouples



r = creerListePref("TestPrefEtu.txt", "TestPrefSpe.txt")
matEtu = r[0]
matSpe = r[1]

gs = algoGS(matEtu, matSpe)
afficherDico(gs)












