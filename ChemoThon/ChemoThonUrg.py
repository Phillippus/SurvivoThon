import streamlit as st
import json
from chemo_utils import bsa, Chemo, ChemoCBDCA, ChemoDDP, show_evidence

# ChemoDDP v urogenitálnej onkológii používa 70 mg/m2 → volaj ChemoDDP(..., ddp_dose=70)

# Function for chemotherapy with flat dosages
def Flatdoser(rbodysurf, chemoType, chemoFlat=None):
    with open('data/' + chemoType, "r") as chemoFile:
        chemoJson = json.loads(chemoFile.read())
    
    # Initialize chemoJson2 to avoid UnboundLocalError
    chemoJson2 = None

    # Only load chemoFlat if it is provided
    if chemoFlat:
        with open('data/' + chemoFlat, "r") as chemoFile2:
            chemoJson2 = json.loads(chemoFile2.read())
    
    st.write("Rozpis chemoterapie:")
    for i in chemoJson["Chemo"]:
        st.write(f"{i['Name']} {round(i['Dosage'], 2)} {i['DosageMetric']}......... {round(i['Dosage'] * rbodysurf, 2)} mg D{i['Day']}")

    # Only display information from chemoJson2 if it is loaded
    if chemoJson2:
        for i in chemoJson2["Chemo"]:
            st.write(f"{i['Name']} {round(i['Dosage'], 2)} {i['DosageMetric']}......... {round(i['Dosage'], 2)} mg D{i['Day']}")
        
    st.write(f"NC {chemoJson['NC']} . deň")
    
    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]

    st.write("D1")
    st.write(chemoJson["Day1"]["Premed"]["Note"])

    for x in range(len(chemoJson["Chemo"])):
        st.write(f"{Day1[x]['Name']} {round(C1[x]['Dosage'] * rbodysurf, 2)} mg {Day1[x]['Inst']}")

    # Process additional instructions if chemoJson2 is loaded
    if chemoJson2:
        DayF1 = chemoJson2["Day1"]["Instructions"]
        CF = chemoJson2["Chemo"]
        for y in range(len(chemoJson2["Chemo"])):
            st.write(f"{DayF1[y]['Name']} {round(CF[y]['Dosage'], 2)} mg {DayF1[y]['Inst']}")

    show_evidence(chemoJson)
    if chemoJson2:
        show_evidence(chemoJson2)

# Main function for urogenital tumors
def urogenital(rbodysurf):
    """Táto funkcia rozpisuje chemoterapie urogenitálnych tumorov"""
    chemo_choice = st.selectbox("Vyberte chemoterapiu:", [" ", "Docetaxel + Prednison", "Mitoxantron + Prednison","Docetaxel + Darolutamid", "Cabazitaxel + Prednison", "Abirateron (CRPC) + Prednison","Abirateron (HSPC) + Prednison","Enzalutamid","Darolutamid","Apalutamid","Pt/ Gemcitabin", "Split-dose Cisplatina D1+D8", "Vinflunin", "BEP",
        "Paclitaxel weekly (urotel / iné)",
        # --- Nové (2026-06) ---
        "Enfortumab vedotín + Pembrolizumab (EV-302, 1. línia urotel)",
        "Olaparib 300 mg BID (HRR+ mCRPC, PROfound)",
        "Nivolumab 240 mg q2w adj. (urotel po cystektómii, CheckMate-274)",
    ])
    
    if chemo_choice == "Docetaxel + Prednison":
        Flatdoser(rbodysurf, "docetaxelprostate.json", "flatprednison3w.json")
    elif chemo_choice == "Mitoxantron + Prednison":
        Flatdoser(rbodysurf, "mitoxantrone.json", "flatprednison3w.json")    
    elif chemo_choice == "Docetaxel + Darolutamid":
        Flatdoser(rbodysurf, "docetaxelprostate.json", "flatdarolutamide3w.json")    
    elif chemo_choice == "Cabazitaxel + Prednison":
        Flatdoser(rbodysurf, "cabazitaxel.json", "flatprednison3w.json")
    elif chemo_choice == "Abirateron (CRPC) + Prednison":
        Flatdoser(1, "flatabirateron.json", "flatprednison4w.json")
    elif chemo_choice == "Abirateron (HSPC) + Prednison":
        Flatdoser(1, "flatabirateron.json", "flatprednisonHSPC4w.json")
    elif chemo_choice == "Enzalutamid":
        Flatdoser(1, "flatenzalutamide4w.json", None)  # Provide None explicitly
    elif chemo_choice == "Apalutamid":
        Flatdoser(1, "flatapalutamide4w.json", None)  # Provide None explicitly    
    elif chemo_choice == "Darolutamid":
        Flatdoser(1, "flatdarolutamide4w.json", None)
    elif chemo_choice == "Pt/ Gemcitabin":
        Ptdecis = st.selectbox("Ktorá platina?", ["Vyberte platinu", "Cisplatina", "Karboplatina"])
        if Ptdecis == "Cisplatina":
            ChemoDDP(rbodysurf, "gemcitabin4w.json", ddp_dose=70)
        elif Ptdecis == "Karboplatina":
            ChemoCBDCA(rbodysurf, "gemcitabin4w.json")
    elif chemo_choice == "Vinflunin":
        vinflu_ps = st.selectbox("PS pacienta / predchádzajúca panvová RT?", ["Vyberte", "PS 0, bez panvovej RT (320 mg/m²)", "PS 1 alebo predchádzajúca panvová RT (280 mg/m²)"])
        if vinflu_ps == "PS 0, bez panvovej RT (320 mg/m²)":
            Chemo(rbodysurf, "vinflunine.json")
        elif vinflu_ps == "PS 1 alebo predchádzajúca panvová RT (280 mg/m²)":
            Chemo(rbodysurf, "vinflunine280.json")
    elif chemo_choice == "BEP":
        Flatdoser(rbodysurf, "BEP.json", "flatbleomycin.json")
    elif chemo_choice == "Split-dose Cisplatina D1+D8":
        total_ddp_dose = round(70 * rbodysurf, 2)
        half_dose = round(total_ddp_dose / 2, 2)
        st.write("### Split-dose Cisplatina D1+D8 (urotelový karcinóm)")
        st.write(f"cisplatina 70 mg/m2 celková dávka ......... {total_ddp_dose} mg")
        st.write(f"D1: cisplatina {half_dose} mg (polovica celkovej dávky)")
        st.write(f"D8: cisplatina {half_dose} mg (zvyšná polovica)")
        st.write("NC 21. deň")
        st.write("D1 + D8 premedikácia:")
        st.write("Palonosetron 0.5mg/Netupitant 300mg (Akynzeo) p.o. 1h pred chemo, Dexametazón 12mg i.v., Pantoprazol 40mg p.o.")
        st.write("Hydratácia: FR 500ml pred cisplatinou, Manitol 10% 250ml po cisplatine")
        b = int(half_dose // 50); c = half_dose % 50
        st.write(f"D1:")
        for i in range(b):
            st.write(f"  cisplatina 50mg v 500ml RR i.v.")
        if c > 0:
            st.write(f"  cisplatina {round(c,1)} mg v 500ml RR i.v.")
        st.write("  Manitol 10% 250ml i.v.")
        st.write(f"D8: opakovať rovnaký postup (cisplatina {half_dose} mg)")
    elif chemo_choice == "Paclitaxel weekly (urotel / iné)":
        Chemo(rbodysurf, "paclitaxelweekly.json")
    # --- Nové (2026-06) ---
    elif chemo_choice == "Enfortumab vedotín + Pembrolizumab (EV-302, 1. línia urotel)":
        if 'weight' in st.session_state:
            weight_val = st.session_state['weight']
            import json as _j
            ev = _j.load(open("data/enfortumab_vedotin.json", encoding="utf-8"))
            ev_dose = min(round(1.25 * weight_val, 2), 125)  # EV-302: strop 125 mg (pacienti ≥100 kg)
            pembro_dose = 200
            st.write("### Enfortumab vedotín + Pembrolizumab (EV-302)")
            ev_cap_note = " (cappované na max 125 mg)" if 1.25 * weight_val > 125 else ""
            st.write(f"enfortumab vedotín 1.25 mg/kg ......... {ev_dose} mg D1, D8{ev_cap_note}")
            st.write(f"pembrolizumab 200 mg flat dose D1")
            st.write("NC 21. deň")
            st.write("D1 - premedikácia:")
            st.write(ev["Day1"]["Premed"]["Note"])
            st.write("D1 - chemoterapia:")
            st.write(f"enfortumab vedotín {ev_dose} mg {ev['Day1']['Instructions'][0]['Inst']}")
            st.write(f"pembrolizumab {pembro_dose} mg {ev['Day1']['Instructions'][1]['Inst']}")
            st.write("D8: enfortumab vedotín bez pembrolizumabu (pembro len D1)")
            show_evidence(ev)
        else:
            st.error("Najprv zadajte hmotnosť.")
    elif chemo_choice == "Olaparib 300 mg BID (HRR+ mCRPC, PROfound)":
        Chemo(rbodysurf, "olaparib_crpc.json")
    elif chemo_choice == "Nivolumab 240 mg q2w adj. (urotel po cystektómii, CheckMate-274)":
        Chemo(rbodysurf, "nivolumab_urothelial_adj.json")

# Main input function for weight and height
def main():
    st.title("ChemoThon UrogenitalSK v 2.3")
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

    if st.button("Vypočítať telesný povrch"):
        if weight and height:
            rbodysurf = bsa(weight, height)
            st.session_state.rbodysurf = rbodysurf
            st.session_state['weight'] = weight
        else:
            st.error("Prosím, zadajte hmotnosť a výšku pre výpočet telesného povrchu.")

    # Always display the BSA if it has been calculated
    if 'rbodysurf' in st.session_state:
        st.write(f"Telesný povrch je: {st.session_state.rbodysurf} m²")

    # Step 2: Display chemotherapy options if BSA is calculated
    if 'rbodysurf' in st.session_state:
        st.write("Teraz vyberte chemoterapiu:")
        urogenital(st.session_state.rbodysurf)

if __name__ == "__main__":
    main()



# ===== Zdroje / Sources (pridané 2026-06, aditívne) =====
with st.expander("📚 Zdroje k režimom / Sources"):
    st.markdown("""**Kľúčové referencie – urogenitálne nádory**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-genitourinary-cancers) · [NCCN](https://www.nccn.org/guidelines/category_1). Vždy overte podľa aktuálnej verzie guidelines a dostupných balení liečiv. Stav: jún 2026.

- **Docetaxel + prednizón (mCRPC)** — TAX327 – Tannock et al., NEJM 2004.
- **Mitoxantrón + prednizón** — Paliatívny – Tannock et al., J Clin Oncol 1996.
- **Docetaxel + darolutamid (mHSPC)** — ARASENS – Smith et al., NEJM 2022.
- **Kabazitaxel + prednizón** — TROPIC – de Bono et al., Lancet 2010; CARD – de Wit et al., NEJM 2019.
- **Abiraterón + prednizón (CRPC)** — COU-AA-301 – de Bono et al., NEJM 2011; COU-AA-302 – Ryan et al., NEJM 2013.
- **Abiraterón + prednizón (HSPC)** — LATITUDE – Fizazi et al., NEJM 2017; STAMPEDE – James et al., NEJM 2017.
- **Enzalutamid** — PREVAIL – Beer et al., NEJM 2014; ARCHES – Armstrong et al., J Clin Oncol 2019.
- **Darolutamid** — ARAMIS (nmCRPC) – Fizazi et al., NEJM 2019.
- **Apalutamid** — SPARTAN (nmCRPC) – Smith et al., NEJM 2018; TITAN (mHSPC) – Chi et al., NEJM 2019.
- **Cisplatina/karboplatina + gemcitabín (urotel)** — von der Maase et al., J Clin Oncol 2000/2005.
- **Vinflunín (urotel, 2. línia)** — Bellmunt et al., J Clin Oncol 2009.
- **BEP (germinatívne nádory)** — Williams et al., NEJM 1987; Einhorn – štandard.

**Aktuálne štandardy na zváženie (zatiaľ mimo nástroja):**
- Enfortumab vedotín + pembrolizumab 1. línia metastatického urotelu – EV-302, NEJM 2024.
- Lutéciové [177Lu]Lu-PSMA-617 pri PSMA+ mCRPC – VISION, NEJM 2021.
- Olaparib pri HRR-mutovanom mCRPC – PROfound, NEJM 2020; + abiraterón PROpel.
- Nivolumab adjuvantne pri vysokorizikovom urotelovom karcinóme – CheckMate-274, NEJM 2021.""")
