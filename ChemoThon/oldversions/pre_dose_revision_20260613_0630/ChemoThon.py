import json

def Chemo(rbodysurf,  chemoType):
    """Táto funkcia rozpisuje jednoduché chemoterapie s priamou umerou"""
    chemoFile = open('data/' + chemoType, "r")
    chemoJson = json.loads(chemoFile.read())
    chemoFile.close()
                   
                   
    for i in chemoJson["Chemo"] :
        print(i["Name"], " ", 
          round(i["Dosage"],2),
          i["DosageMetric"],".........",
          round(i["Dosage"]*rbodysurf,2),
          "mg D",
          i["Day"])
        
    print ("""         
                       NC""", chemoJson["NC"], """. deň
                                            """)
    
    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]
    
    print("                                     D1")
    print (chemoJson["Day1"]["Premed"]["Note"])
    
    for x in range(len(chemoJson["Chemo"])):
        print (Day1[x]["Name"], round(C1[x]["Dosage"]*rbodysurf,2),"mg", Day1[x]["Inst"] )
    
def ChemoMass(weight, chemoType):
    """Táto funkcia rozpisuje chemoterapie/ biologika podľa hmotnosti"""
    chemoFile = open(chemoType, "r")
    chemoJson = json.loads(chemoFile.read())
    chemoFile.close()
                   
                   
    for i in chemoJson["Chemo"] :
        print(i["Name"], " ", 
          round(i["Dosage"],2),
          i["DosageMetric"],".........",
          round(i["Dosage"]*weight,2),
          "mg D",
          i["Day"])
        
    print ("""         
                       NC""", chemoJson["NC"], """. deň
                                            """)
    
    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]
    
    print("                                     D1")
    print (chemoJson["Day1"]["Premed"]["Note"])
    
    for x in range(len(chemoJson["Chemo"])):
        print (Day1[x]["Name"], round(C1[x]["Dosage"]*weight,2),"mg", Day1[x]["Inst"] )
        
def Chemo5FU(rbodysurf,  chemoType):
    """Táto funkcia rozpisuje chemoterapie s kontinualnym 5FU"""
    chemoFile = open('data/'+chemoType, "r")
    chemoJson = json.loads(chemoFile.read())
    chemoFile.close()
               
                
                   
    for i in chemoJson["Chemo"] :
        print(i["Name"], " ", 
          round(i["Dosage"],2),
          i["DosageMetric"],".........",
          round(i["Dosage"]*rbodysurf,2),
          "mg D",
          i["Day"])
        
    
    
    if chemoType=="FLOT.json":
        dos5FU= 2600
        dos15FU=2600
        day5FU= "24 hodin"
        day15FU="24 hodin"
    
    elif chemoType=="mtc5FU.json":
        dos5FU= 1000
        dos15FU= 1000
        day5FU= "D1-4"
        day15FU="24 hodin"
    
    else:
        dos5FU= 2400
        dos15FU= 1200
        day5FU= "48 hodin"
        day15FU="24 hodin"
        
    print("""5-fluoruracil""",dos5FU,"""mg/m2......""",rbodysurf*dos5FU,"""mg/""", day5FU)
    print ("""         
                       NC""", chemoJson["NC"], """. deň
                                            """)
       
    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]
    
    print("                                     D1")
    print (chemoJson["Day1"]["Premed"]["Note"])
    
    for x in range(len(chemoJson["Chemo"])):
        print (Day1[x]["Name"], round(C1[x]["Dosage"]*rbodysurf,2),"mg", Day1[x]["Inst"] )
    print("""5-fluoruracil""",rbodysurf*dos15FU,"""mg/kivi""",day15FU)
            
                   
def ChemoDDP(rbodysurf,  chemoType):
    """Táto funkcia slúži pre chemoterapie s DDP"""
       
    chemoFile = open('data/'+chemoType, "r")
    chemoJson = json.loads(chemoFile.read())
    chemoFile.close()
    
    print("DDP 80mg/m2................",80*rbodysurf,"mg  D1")
    for i in chemoJson["Chemo"] :
        print(i["Name"], " ", 
          i["Dosage"], 
          i["DosageMetric"], " .....",
          round(i["Dosage"]*rbodysurf,2),
          "mg D",
          i["Day"])
        
    print ("""
                   NC""", chemoJson["NC"], """. deň
           """)
    
    print("""                                  
                                          D1
                                          """)
    print ("1. ",chemoJson["Day1"]["Premed"]["Note"])

    a=round(80*rbodysurf,2)
    b=a//50
    c=a%50
    rng=int(b)
    
    for ordo in range(2,rng+2):
        print(ordo, """. Cisplatina 50mg v 500ml RR iv""")
        ordo+=1
    print(ordo,""". Cisplatina""",int(c),"""mg v 500ml RR iv""")
    print(ordo+1,""". Manitol 10% 250ml iv""")
    
    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]
      
    for x in range(len(chemoJson["Chemo"])):
        print (ordo+2,".",Day1[x]["Name"], C1[x]["Dosage"]*rbodysurf,"mg", Day1[x]["Inst"] )
        
def ChemoCBDCA(rbodysurf,chemoType):
    """Táto funkcia slúži pre rozpis chemoterapie obsahujúcu karboplatinu"""
    chemoFile = open('data/'+chemoType, "r")
    chemoJson = json.loads(chemoFile.read())
    chemoFile.close()
    
    while True:
        try:
            CrCl=int(input("Zadajte hodnotu clearance v ml/min     "))
            assert 0 < CrCl < 250
            
        except ValueError:
            print("Musíte zadať celé číslo!" )
        except AssertionError:
            print("Povolené hodnoty sú od 1 do 250!")
        else:
            break
        
    while True:
        try:
            AUC=int(input("Zadajte hodnotu AUC 2-6    "))
            assert 1 < AUC < 7
            
        except ValueError:
            print("Musíte zadať celé číslo!" )
        except AssertionError:
            print("Povolené hodnoty sú od 2 do 6!")
        else:
            break    
    
    print("CBDCA AUC",AUC,"............",(CrCl+25)*AUC,"mg  D1")        
    for i in chemoJson["Chemo"] :
        print(i["Name"], " ", 
          i["Dosage"], 
          i["DosageMetric"], " .....",
          i["Dosage"]*rbodysurf,
          "mg D",
          i["Day"])
        
    print ("""         
                       NC""", chemoJson["NC"], """. deň
                                            """)
    
    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]
    
    print("""                                   
                                        D1
                                        """)
    print (chemoJson["Day1"]["Premed"]["Note"])
    print("CBDCA",(CrCl+25)*AUC,"mg v 500ml FR iv" )
    for x in range(len(chemoJson["Chemo"])):
        print (Day1[x]["Name"], round(C1[x]["Dosage"]*rbodysurf,2),"mg", Day1[x]["Inst"] )


def platinum5FU(rbodysurf):
    """Táto chemoterapia sluzi na rozpis chemoterapie s platinou a 5FU"""
    
    a=80*rbodysurf
    b=a//50
    c=a%50
    rng=int(b)
    
       
    whichPt=str(input(""" Ktorá platina?
a) Cisplatina 
b) Karboplatina\n"""))
    
    if whichPt=="a":
        print("""DDP 80mg/m2................""",80*rbodysurf,"""mg  D1""")
        print("""5-fluoruracil 1000mg/m2.........""", 1000*rbodysurf,"""mg D1-D4""")
        print("""      
                                             NC 21.deň
                                                          
                                                          D1
                                                          
1. Dexametazon 8mg iv, Pantoprazol 40 mg p.o., Ondasetron 8mg v 250ml FR iv""")
        for ordo in range(2,rng+2):
            print(ordo, """. Cisplatina 50mg v 500ml RR iv""")
            ordo+=1
        print(ordo,""". Cisplatina""",int(c),"""mg v 500ml RR iv""")
        print(ordo+1,""". Manitol 10% 250ml iv""")
        print(ordo+2,""". 5-fluoruracil""",rbodysurf*1000,"""mg na 24 hodin/ kivi""")
        
    elif whichPt=="b":
        while True:
            try:
                CrCl=int(input("Zadajte hodnotu clearance v ml/min     "))
                assert 0 < CrCl < 250
            
            except ValueError:
                print("Musíte zadať celé číslo!" )
            except AssertionError:
                print("Povolené hodnoty sú od 1 do 250!")
            else:
                break
        
        while True:
            try:
                AUC=int(input("Zadajte hodnotu AUC 2-6    "))
                assert 1 < AUC < 7
            
            except ValueError:
                print("Musíte zadať celé číslo!" )
            except AssertionError:
                print("Povolené hodnoty sú od 2 do 6!")
            else:
                break    
    
        print("""CBDCA AUC""",AUC,"""............""",(CrCl+25)*AUC,"""mg  D1
5-fluoruracil 1000mg/m2..............""",rbodysurf*1000,"""mg  D1-D4""")     
        print("""      
                                             NC 21.deň
                                                          
                                                          D1
Dexametazon 8mg iv, Pantoprazol 40 mg p.o., Ondasetron 8mg v 250ml FR iv""")
        print("""CBDCA AUC""",AUC,"""............""",(CrCl+25)*AUC,"""mg  D1""") 
        print("""5-fluoruracil""",rbodysurf*1000,"""mg na 24 hodin/ kivi""")

def Flatdoser(rbodysurf,chemoType, chemoFlat):
    chemoFile = open('data/'+chemoType, "r")
    chemoJson = json.loads(chemoFile.read())
    chemoFile.close()
    
    chemoFile2 = open('data/'+chemoFlat, "r")
    chemoJson2 = json.loads(chemoFile2.read())
    chemoFile2.close()
    
    
    
    for i in chemoJson["Chemo"] :
        print(i["Name"], " ", 
        round(i["Dosage"],2),
        i["DosageMetric"],".........",
        round(i["Dosage"]*rbodysurf,2),
        "mg D",
        i["Day"])
    
    for i in chemoJson2["Chemo"] :
        print(i["Name"], " ",
        round(i["Dosage"],2),
        i["DosageMetric"],".........",
        round(i["Dosage"],2),
        "mg D",
        i["Day"])
        
    print ("""         
                       NC""", chemoJson["NC"], """. deň
                                            """)
    
    Day1 = chemoJson["Day1"]["Instructions"]
    DayF1= chemoJson2["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]
    CF = chemoJson2["Chemo"]
    
    print("                                     D1")
    print (chemoJson["Day1"]["Premed"]["Note"])
    
    for x in range(len(chemoJson["Chemo"])):
        print (Day1[x]["Name"], round(C1[x]["Dosage"]*rbodysurf,2),"mg", Day1[x]["Inst"] )
    for y in range(len(chemoJson2["Chemo"])):
        print (DayF1[y]["Name"], round(CF[y]["Dosage"]),"mg", DayF1[y]["Inst"] )        

def ChemoIfo(rbodysurf,dose, otherCHT):
    ifo=int(dose*rbodysurf)
    mesna=ifo*0.8
    ifocycle=ifo//2000
    mesnacycle=ifocycle+1
    iforemnant=ifo%2000
    mesnainit=1200
    mesnaend=800
    
    
    
    if otherCHT==True:
        print("""epirubicin 60mg/m2........""",60*rbodysurf,"""mg D1, D2
ifosfamid 3000mg/m2..........""",ifo,"""mg D1,D2,D3
mesna 0.8 x ifosfamid........""",mesna,"""mg D1,D2,D3
              
                                        NC 21. den
                                                        
                                                        D1
                                                            """)
        
        print("""Ondasetron 8mg iv, Dexametazon 8mg iv, Pantoprazol 40mg p.o.""")
        print("""Epirubicin""",60*rbodysurf,"""mg v 500ml FR iv""")
        print("""MESNA""",mesnainit,"""mg v 100ml FR /4hodiny""")
        if iforemnant>200:
            mesnacont=(mesna-2000)//ifocycle
            for cycifo in range(0,ifocycle):
                print("""Ifosfamid 2000mg v 500ml FR iv""")
                print("""MESNA""",mesnacont,"""mg v 100ml FR iv/ 4 hodiny""")
            print("""Ifosfamid""",iforemnant,"""mg 500ml FR iv""")
            print("""MESNA 800mg v 100ml FR iv/ 4 hodiny""")   
        else: 
            mesnacont=(mesna-1200)//ifocycle
            for cycifo in range(0,ifocycle):
                print("""Ifosfamid 2000mg v 500ml FR iv""")
                print("""MESNA""",mesnacont,"""mg v 100ml FR iv/ 4 hodiny""")
    
   
   
    else:
        print("""ifosfamid 3000mg/m2..........""",ifo,"""mg D1,D2,D3
mesna 0.8 x ifosfamid........""",mesna,"""mg D1,D2,D3
              
                                        NC 21. den
                                                        
                                                        D1
                                                            """)
        
        print("""Ondasetron 8mg iv, Dexametazon 8mg iv, Pantoprazol 40mg p.o.""")
        print("""MESNA""",mesnainit,"""mg v 100ml FR /4hodiny""")
        if iforemnant>200:
            mesnacont=(mesna-2000)//ifocycle
            for cycifo in range(0,ifocycle):
                print("""Ifosfamid 2000mg v 500ml FR iv""")
                print("""MESNA""",mesnacont,"""mg v 100ml FR iv/ 4 hodiny""")
            print("""Ifosfamid""",iforemnant,"""mg 500ml FR iv""")
            print("""MESNA 800mg v 100ml FR iv/ 4 hodiny""")   
        else: 
            mesnacont=(mesna-1200)//ifocycle
            for cycifo in range(0,ifocycle):
                print("""Ifosfamid 2000mg v 500ml FR iv""")
                print("""MESNA""",mesnacont,"""mg v 100ml FR iv/ 4 hodiny""")
                

def DHAP(rbodysurf):
    """Táto funkcia je len a len pre DHAP"""
    DDP=round(rbodysurf*100,2)
    cycle=DDP//50
    remnant=DDP%50
    iremnant=int(remnant)
    icycle=int(cycle)
    print("""cisplatina 100mg/m2........""",100*rbodysurf,"""mg D1
cytarabin 2000mg/m2 BID.......""",2000*rbodysurf,"""mg a 12 hodin D2
prednison 40mg ....................40mg D1-D4
          
                                        NC 21. deň
                                                  
                                            D1
                                            
1. Ondasetron 8mg v 250ml FR iv, Dexametazon 8mg iv, Pantoprazol 40mg p.o.""")
    
    for ordo in range(2,icycle+2):
        print(ordo,""". cisplatina 50mg v 500ml RR iv""")
        ordo+=1
    if iremnant>0:    
        print(ordo,""". cisplatina """,iremnant,"""mg v 500ml RR iv""")
        print(ordo+1,""". manitol 10% 250ml iv""")
        print(ordo+2,""". prednison 40mg tbl p.o. """)
        
    else:
        print(ordo,""". manitol 10% 250ml iv""")
        print(ordo+1,""". prednison 40mg tbl p.o. """)
    

             
              
    
def hematology(rbodysurf):
    """Tato funkcia ponuka chemoterapie pouzivane v hematoonkologii"""
    hem=str(input("""Aku chemoterapiu chcete podat?  
a) ABVD
b) CHOP
c) miniCHOP
d) DHAP
e) bendamustin
f) GemOx
g) Rituximab\n"""))
    
    if hem=="a":
        Chemo(rbodysurf,"ABVD.json")
    elif hem=="b":
        Flatdoser(rbodysurf,"CHOP.json","flatvincristin.json")
    elif hem=="c":
        Flatdoser(rbodysurf,"miniCHOP.json","flatminivincristin.json" )
    elif hem=="d":
        DHAP(rbodysurf)
    elif hem=="e":
        Chemo(rbodysurf,"bendamustin.json")
    elif hem=="f":
        Chemo(rbodysurf,"Gemox.json")
    elif hem=="g":
        Chemo(rbodysurf,"rituximab.json")
    else:
        print("""Musite zadat a-g!""")
        hematology(rbodysurf)        

def breast(rbodysurf):
    """Tato funkcia ponuka chemoterapie pouzivane v liecbe karcinomu prsnika"""
    brs=str(input("""Aku chemoterapiu chcete podat?  
a) EC
b) AC
c) dd-AC + G-CSF
d) docetaxel + G-CSF
e) paclitaxel
f) kapecitabin
g) gemcitabin
h) vinorelbin p.o. weekly
i) eribulin
j) peg- doxorubicin
k) TD-M1\n"""))
    
    if brs=="a":
    	Chemo(rbodysurf,"EC.json")
    elif brs=="b":
        Chemo(rbodysurf, "AC.json")
    elif brs=="c":
        Chemo(rbodysurf,"dd-AC.json")
    elif brs=="d":
        Chemo(rbodysurf,"docetaxelbreast.json")
    elif brs=="e":
        Chemo(rbodysurf,"paclitaxelweekly.json")
    elif brs=="f":
        Chemo(rbodysurf,"capecitabine.json")
    elif brs=="g":
        Chemo(rbodysurf,"gemcitabine.json")
    elif brs=="h":
        Chemo(rbodysurf,"vinorelbinweekly.json")
    elif brs=="i":
        Chemo(rbodysurf,"eribulin.json")
    elif brs=="j":
        Chemo(rbodysurf,"pegdoxo.json")
    elif brs=="k":
        Chemo(rbodysurf,"TDM1.json")
    else:   
        print("""Musite zadat a-k!""")
        breast(rbodysurf)

def lung(rbodysurf):
    """Tato funkcia ponuka chemoterapie pouzivane v liecbe karcinomu pluc"""
    lng=str(input("""Aku chemoterapiu chcete podat?
a)CBDCA + paclitaxel
b)CBDCA + pemetrexed
c)DDP + gemcitabine
d)CBDCA + gemcitabine
e)DDP + etoposide
f)Topotecan + G-CSF\n"""))
    
    if lng=="a":
        ChemoCBDCA(rbodysurf,"paclitaxel3weekly.json")
    elif lng=="b":    
        ChemoCBDCA(rbodysurf,"pemetrexed.json")
    elif lng=="c":
        ChemoDDP(rbodysurf,"gemcitabinDDP.json")
    elif lng=="d":
        ChemoCBDCA(rbodysurf,"gemcitabinCBDCA.json")
    elif lng=="e":
        ChemoDDP(rbodysurf,"etoposide.json")
    elif lng=="f":
        Chemo(rbodysurf,"topotecan.json")
    else: 
        print("""Musite zadat a-f!""")
        lung(rbodysurf)
        
def firstcetux(rbodysurf):
    ctx=str(input("Prvé podanie cetuximabu (a/n)?  "))
    if ctx=="a":
        Chemo(rbodysurf,"1cetuximab.json")
    elif ctx=="n":
        Chemo(rbodysurf,"elsecetuximab.json")
        
def colorectal(rbodysurf, weight):
    """Táto funkcia rozpisuje chemoterapie pouzivane v liecbe kolorektalneho karcinomu"""
    crc=str(input("""Aku chemoterapiu chcete podat?
a)FOLFOX
b)FOLFIRI
c)CapOX
d)CapIri
e)capecitabine 
f)bevacizumab3W
g)bevacizumab2w
h)cetuximab
i)panitumumab
j)trifluridine/tipiracil
k)irinotecan
l)FOLFIRINOX\n"""))
    
    if crc=="a":
        Chemo5FU(rbodysurf,"data/FOLFOX.json")
    elif crc=="b":
        Chemo5FU(rbodysurf,"FOLFIRI.json")
    elif crc=="c":
        Chemo(rbodysurf,"Capox.json")
    elif crc=="d":
        Chemo(rbodysurf,"Capiri.json")
    elif crc=="e":
        Chemo(rbodysurf,"capecitabine.json")
    elif crc=="f":
        ChemoMass(weight,"bevacizumab3w.json")
    elif crc=="g":
        ChemoMass(weight,"bevacizumab2w.json")
    elif crc=="h":
        ctx=str(input("Prvé podanie cetuximabu (a/n)?  "))
        if ctx=="a":
            Chemo(rbodysurf,"1cetuximab.json")
        elif ctx=="n":
            Chemo(rbodysurf,"elsecetuximab.json")
        else:
            print("Ano alebo nie!")
            colorectal(rbodysurf)
            
            
    elif crc=="i":
        ChemoMass(weight,"panitumumab.json")
    elif crc=="j":
        Chemo(rbodysurf,"tritipi.json")
    elif crc=="k":
        Chemo(rbodysurf,"irinotecan.json")
    elif crc=="l":
        Chemo5FU(rbodysurf,"FOLFIRINOX.json")
    else:
        print("""Musíte zadať a-l!! """)
        colorectal(rbodysurf)
            
def gastrointestinal(rbodysurf):
    """Táto funkcia rozpisuje chemoterapie pouzivane v liecbe gastrointestinalnych malignit"""
    git=str(input("""Aku chemoterapiu chcete podat?
a)Pt/5-FU
b)FLOT
c)EOX
d)paclitaxel weekly
e)FOLFIRINOX
f)gemcitabin/ capecitabine
g)gemcitabin/ nab- paclitaxel
h)peglip irinotekan/ 5-FU
i)gemcitabin
j)mitomycin/ 5-FU\n"""))
    
    if git=="a":
        platinum5FU(rbodysurf)
    elif git=="b":
        Chemo5FU(rbodysurf,"FLOT.json")
    elif git=="c":
        Chemo(rbodysurf,"EOX.json")
    elif git=="d":
        Chemo(rbodysurf,"paclitaxelweekly.json")
    elif git=="e":
        Chemo5FU(rbodysurf,"FOLFIRINOX.json")
    elif git=="f":
        Chemo(rbodysurf,"gemcap.json")
    elif git=="g":
        Chemo(rbodysurf,"gemnabpcl.json")
    elif git=="h":
        Chemo5FU(rbodysurf,"peglipiri5FU.json")
    elif git=="i":
        Chemo(rbodysurf,"gemcitabine4w.json")
    elif git=="j":
        Chemo5FU(rbodysurf,"mtc5FU.json")
    else:
        print("""Musíte zadať a-j!! """)
        gastrointestinal(rbodysurf)
        
def headandneck(rbodysurf): 
    """Táto funkcia rozpisuje chemoterapie pouzivane v liecbe nadorov hlavy a krku"""
    han=str(input("""Aku chemoterapiu chcete podat?
a)Pt/5-FU
b)cetuximab
c)paclitaxel weekly
d)metotrexat\n"""))
            
    if han=="a":       
        platinum5FU(rbodysurf)
    elif han=="b":
        ctx=str(input("Prvé podanie cetuximabu (a/n)?  "))
        if ctx=="a":
            Chemo(rbodysurf,"1cetuximab.json")
        elif ctx=="n":
            Chemo(rbodysurf,"elsecetuximab.json")
        else:
            print("Ano alebo nie!")
            headandneck(rbodysurf) 
    elif han=="c":
        Chemo(rbodysurf,"paclitaxelweekly.json")
    elif han=="d":
        Chemo(rbodysurf,"metotrexate.json")       
    else:
        print("""Musíte zadať a-d!! """)
        headandneck(rbodysurf)

def sarcnet(rbodysurf):
    """Táto funkcia rozpisuje chemoterapie a biologickú liečbu sarkómov a CNS a neuroendokrinnych tumorov"""
    
    snet=str(input("""Aku chemoterapiu chcete podat?
a)ifosfamid/ epirubicin
b)ifosfamid
c)trabectedin
d)doxorubicin
e)paclitaxel weekly
f)CBDCA/paclitaxel
g)DDP/etoposid
h)CBDCA/etoposid
i)dakarbazin 5 dnovy
j)temozolomid 
k)lomustine (CCNU)\n"""))

    if snet=="a":
        ChemoIfo(rbodysurf,3000,True)
    elif snet=="b":
        ChemoIfo(rbodysurf,3000,False)
    elif snet=="c":
        Chemo(rbodysurf,"trabectedin.json")
    elif snet=="d":
        Chemo(rbodysurf,"doxorubicin.json")
    elif snet=="e":
        Chemo(rbodysurf,"paclitaxelweekly.json")
    elif snet=="f":
        ChemoCBDCA(rbodysurf,"paclitaxel3weekly.json")    
    elif snet=="g":
        ChemoDDP(rbodysurf,"etoposide.json")
    elif snet=="h":
        ChemoCBDCA(rbodysurf,"etoposide.json")
    elif snet=="i":
        Chemo(rbodysurf,"dacarbazine.json")
    elif snet=="j":
        temozolomide=str(input("""Temozolomid je:
a) v ramci chemoRAT
b) solo 150mg/m2
c) solo 200mg/m2\n"""))
        if temozolomide=="a":
            Chemo(rbodysurf,"temozolomideRAT.json")
        elif temozolomide=="b":
            Chemo(rbodysurf,"temozolomide150.json")
        elif temozolomide=="c":
            Chemo(rbodysurf,"temozolomide200.json")
        else:
            print("Zadajte a, b alebo c!!")
            sarcnet(rbodysurf)
    elif snet=="k":
        Chemo(rbodysurf,"CCNU.json")
    else:
        print("""Musíte zadať a-k!!""")
        sarcnet(rbodysurf)
        
        

def urogenital(rbodysurf):
    """Táto funkcia rozpisuje chemoterapie urogenitálnych tumorov"""
    urog=str(input("""Aku chemoterapiu chcete podať? 
a) docetaxel + prednison
b) cabazitaxel + prednison
c) abirateron + prednison
d) Pt/ gemcitabin
e) vinflunin
f) BEP\n"""))
    
    
    if urog=="a":
        Flatdoser(rbodysurf, "docetaxelprostate.json","flatprednison3w.json")
    elif urog=="b":
        Flatdoser(rbodysurf, "cabazitaxel.json","flatprednison3w.json") 
    elif urog=="c":
        Flatdoser(1,"flatabirateron.json","flatprednison4w.json")
    elif urog=="d":
        Ptdecis=str(input(""" Ktorá platina? 
a) Cisplatina
b) Karboplatina\n"""))
        if Ptdecis=="a":
            ChemoDDP(rbodysurf, "gemcitabin4w.json")
        elif Ptdecis=="b":
            ChemoCBDCA(rbodysurf,"gemcitabin4w.json")
        else:
            print("""Musíte zadať "a" alebo "b"!!""")
            urogenital(rbodysurf) 
    elif urog=="e":
        Chemo(rbodysurf, "vinflunine.json")
    elif urog=="f":
        Flatdoser(rbodysurf, "BEP.json", "flatbleomycin.json")   
    else:
        print("""Musíte zadať a-f!!""")
        urogenital(rbodysurf)
                 
def gynecology(rbodysurf):
    """Táto funkcia rozpisuje chemoterapie gynekologickych tumorov"""
    gyn=str(input("""Akú chemoterapiu chcete podať?
a)CBDCA/ paclitaxel
b)Topotecan + G-CSF
c)PEG-doxorubicin
d)CBDCA/ PEG-doxorubicin
e)CBDCA/ gemcitabin\n"""))
    
    if gyn=="a":
        ChemoCBDCA(rbodysurf,"paclitaxel3weekly.json")
    elif gyn=="b":
        Chemo(rbodysurf,"topotecan.json")
    elif gyn=="c":
        Chemo(rbodysurf,"pegdoxo.json")
    elif gyn=="d":
        ChemoCBDCA(rbodysurf,"PEGdoxo30.json")
    elif gyn=="e":
        ChemoCBDCA(rbodysurf,"gemcitabinCBDCA.json")
    else:
        print("""Musíte zadať a-e!!""")
        gynecology(rbodysurf)

        
            
def diagnosis(rbodysurf,weight):
    """Tato funkcia urobi prvu triaz podla diagnozy"""
    while True:
        try:
            x=int(input("""Aku diagnozu idete liecit?  
1.) hematologicke malignity
2.) karcinom prsnika
3.) karcinom pluc
4.) kolorektalny karcinom
5.) ine GIT malignity
6.) karcinom hlavy a krku
7.) sarkomy, NET a CNS tumory
8.) urogenitalne malignity
9.) gynekologicke malignity
"""))
            assert 0 < x < 10
  
        except ValueError:
            print("Musite zadat cele cislo" )
            diagnosis(rbodysurf,weight)
                    
        except AssertionError:
            print("Povolene hodnotry su od 1 do 9!")
            diagnosis(rbodysurf,weight)
        else:
            break
        
    
    if x==1:
        hematology(rbodysurf)
    elif x==2:
        breast(rbodysurf)
    elif x==3:
        lung(rbodysurf)
    elif x==4:
        colorectal(rbodysurf,weight)
    elif x==5:
        gastrointestinal(rbodysurf)
    elif x==6:
        headandneck(rbodysurf)
    elif x==7:
        sarcnet(rbodysurf)
    elif x==8:
        urogenital(rbodysurf)
    elif x==9:
        gynecology(rbodysurf)

     

def bsa(weight, height):
    bodysurf= (weight**0.425)*(height**0.725)*0.007184
    rbodysurf= round(bodysurf,2)
    print("""Telesný povrch je:""", rbodysurf,"""m2
                                          """)
    diagnosis(rbodysurf, weight)
    
def inpt():
    
    while True:
        try:
            w=int(input("Zadajte hmotnosť (kg):   "))
            assert 0 < w < 250
            
        except ValueError:
            print("Musíte zadať celé číslo!" )
        except AssertionError:
            print("Povolené hodnoty sú od 1 do 250!")
        else:
            break
       
    while True:
        try:
            h=int(input("Zadajte výšku (cm):     "))
            assert 0 < h < 250
            
        except ValueError:
            print("Musíte zadať celé číslo!" )
        
        except AssertionError:
            print("Povolené hodnoty sú od 1 do 250!")
        else:
            break
            
           
    bsa(w, h)
    
print("""-------Vitajte v programe ChemoThon v1.0 !! -------------------
Program rozpisuje najbežnejšie chemoterapie podľa povrchu alebo hmotnosti
Dávky je nutné upraviť podľa aktuálne dostupných balení liečiv
Autor nezodpovedá za prípadné škody spôsobené jeho použitím !
Pripomienky posielajte na filip.kohutek@fntn.sk
Program kedykoľvek ukončíte kombináciou CTRL-C """)
inpt()