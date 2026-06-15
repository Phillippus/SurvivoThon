import streamlit as st
import json
from chemo_utils import bsa, Chemo

# Function for platinum + 5FU chemotherapy
def platinum5FU(rbodysurf):
    """Táto chemoterapia slúži na rozpis chemoterapie s platinou a 5FU"""
    
    a = 80 * rbodysurf
    b = a // 50
    c = a % 50
    rng = int(b)
    
    whichPt = st.selectbox("Ktorá platina?", ["Vyberte platinu", "Cisplatina", "Karboplatina"])
    
    if whichPt == "Cisplatina":
        st.write(f"DDP 80mg/m2................ {80 * rbodysurf} mg  D1")
        st.write(f"5-fluoruracil 1000mg/m2......... {1000 * rbodysurf} mg D1-D4")
        st.write("""
                                             NC 21. deň

                                             D1
        """)
        st.write("1. Palonosetron 0.5mg/Netupitant 300mg (Akynzeo) p.o. 1h pred chemo, Dexametazón 12mg i.v., Pantoprazol 40mg p.o.")
        next_n = 2
        for _ in range(rng):
            st.write(f"{next_n}. Cisplatina 50mg v 500ml RR iv")
            next_n += 1
        if c > 0:
            st.write(f"{next_n}. Cisplatina {round(c, 2)} mg v 500ml RR iv")
            next_n += 1
        st.write(f"{next_n}. Manitol 10% 250ml iv")
        next_n += 1
        st.write(f"{next_n}. 5-fluoruracil {rbodysurf * 1000} mg na 24 hodín/kivi")
        
    elif whichPt == "Karboplatina":
        CrCl = st.number_input("Zadajte hodnotu clearance v ml/min", min_value=1, max_value=250, value=None, step=1)
        AUC = st.number_input("Zadajte hodnotu AUC 2-6", min_value=2, max_value=6, value=None, step=1)
        
        if CrCl is not None and AUC is not None:
            st.write(f"CBDCA AUC {AUC}............ {(CrCl + 25) * AUC} mg  D1")
            st.write(f"5-fluoruracil 1000mg/m2.............. {rbodysurf * 1000} mg  D1-D4")     
            st.write("""
                                                 NC 21. deň
                                                              
                                                 D1
            """)
            st.write("Palonosetron 0.5mg/Netupitant 300mg (Akynzeo) p.o. 1h pred chemo, Dexametazón 12mg i.v., Pantoprazol 40mg p.o.")
            st.write(f"CBDCA {(CrCl + 25) * AUC} mg v 500ml FR iv")
            st.write(f"5-fluoruracil {rbodysurf * 1000} mg na 24 hodín/kivi")

# Function for biweekly cetuximab 500mg/m²
def cetuximabBiweekly(rbodysurf):
    """Cetuximab 500mg/m² podávaný každé 2 týždne"""
    with open('data/cetuximab2w500.json', 'r') as chemoFile:
        chemoJson = json.loads(chemoFile.read())

    st.write("Rozpis chemoterapie:")
    for i in chemoJson["Chemo"]:
        dose = round(i["Dosage"] * rbodysurf, 2)
        st.write(f"{i['Name']} {i['Dosage']} {i['DosageMetric']} .......... {dose} mg D{i['Day']}")

    st.write(f"NC {chemoJson['NC']} . deň")

    st.write("D1 - premedikácia:")
    st.write(chemoJson["Day1"]["Premed"]["Note"])

    st.write("D1 - chemoterapia:")
    for x in range(len(chemoJson["Chemo"])):
        dose = round(chemoJson["Chemo"][x]["Dosage"] * rbodysurf, 2)
        st.write(f"{chemoJson['Day1']['Instructions'][x]['Name']} {dose} mg {chemoJson['Day1']['Instructions'][x]['Inst']}")# Function for basic chemotherapy

# Function for head and neck cancer chemotherapy
def headandneck(rbodysurf): 
    """Táto funkcia rozpisuje chemoterapie používané v liečbe nádorov hlavy a krku"""
    chemo_choice = st.selectbox("Vyberte chemoterapiu:", [
        "Vyberte chemoterapiu",
        "Pt/5-FU",
        "Cetuximab (weekly)",
        "Cetuximab (biweekly)",
        "Paclitaxel weekly",
        "Metotrexat",
        # --- Nové (2026-06) ---
        "Pembrolizumab (R/M HNSCC, KEYNOTE-048)",
        "Nivolumab 240 mg q2w (R/M HNSCC platina-refr., CheckMate-141)",
    ])
    
    if chemo_choice == "Pt/5-FU":
        platinum5FU(rbodysurf)
    elif chemo_choice == "Cetuximab (weekly)":
        ctx_choice = st.selectbox("Prvé podanie cetuximabu?", ["Vyberte možnosť", "Áno", "Nie"])
        if ctx_choice == "Áno":
            Chemo(rbodysurf, "1cetuximab.json")
        elif ctx_choice == "Nie":
            Chemo(rbodysurf, "elsecetuximab.json")
    elif chemo_choice == "Cetuximab (biweekly)":
        cetuximabBiweekly(rbodysurf)
    elif chemo_choice == "Paclitaxel weekly":
        Chemo(rbodysurf, "paclitaxelweekly.json")
    elif chemo_choice == "Metotrexat":
        Chemo(rbodysurf, "metotrexate.json")
    elif chemo_choice == "Pembrolizumab (R/M HNSCC, KEYNOTE-048)":
        Chemo(rbodysurf, "pembrolizumab_hnscc.json")
    elif chemo_choice == "Nivolumab 240 mg q2w (R/M HNSCC platina-refr., CheckMate-141)":
        Chemo(rbodysurf, "nivolumab_hnscc.json")

# Main input function for weight and height
def main():
    st.title("ChemoThon Head and NeckSK v2.2")
    st.write("""
    Program rozpisuje najbežnejšie chemoterapie podľa povrchu alebo hmotnosti.
    Dávky je nutné upraviť podľa aktuálne dostupných balení liečiv.
    Autor nezodpovedá za prípadné škody spôsobené jeho použitím!
    Pripomienky posielajte na filip.kohutek@fntn.sk
    Program kedykoľvek ukončíte zatvorením okna.
    """)

    # Step 1: Input weight and height
    weight = st.number_input("Zadajte hmotnosť (kg):", min_value=1, max_value=250, value=None)
    height = st.number_input("Zadajte výšku (cm):", min_value=1, max_value=250, value=None)

    if st.button("Vypočítať telesný povrch") and weight is not None and height is not None:
        rbodysurf = bsa(weight, height)
        st.session_state.rbodysurf = rbodysurf

    # Always display the BSA if it has been calculated
    if 'rbodysurf' in st.session_state:
        st.write(f"Telesný povrch je: {st.session_state.rbodysurf} m²")

    # Step 2: Display chemotherapy options if BSA is calculated
    if 'rbodysurf' in st.session_state:
        st.write("Teraz vyberte chemoterapiu:")
        headandneck(st.session_state.rbodysurf)

if __name__ == "__main__":
    main()



# ===== Zdroje / Sources (pridané 2026-06, aditívne) =====
with st.expander("📚 Zdroje k režimom / Sources"):
    st.markdown("""**Kľúčové referencie – nádory hlavy a krku**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-head-and-neck-cancers) · [NCCN](https://www.nccn.org/guidelines/category_1). Vždy overte podľa aktuálnej verzie guidelines a dostupných balení liečiv. Stav: jún 2026.

- **Pt / 5-FU + cetuximab** — EXTREME – Vermorken et al., NEJM 2008.
- **Cetuximab (weekly / biweekly)** — Bonner et al., NEJM 2006 (+RT); EXTREME pre weekly.
- **Paklitaxel weekly** — Paliatívna monoterapia – NCCN Head & Neck.
- **Metotrexát** — Štandardná paliatívna 2. línia – Forastiere et al., J Clin Oncol 1992.

**Aktuálne štandardy na zváženie (zatiaľ mimo nástroja):**
- Pembrolizumab ± chemo 1. línia R/M HNSCC (CPS≥1) – KEYNOTE-048, Lancet 2019.""")
