import streamlit as st
from chemo_utils import bsa, Chemo, ChemoCBDCA, ChemoDDP

# Function for chemotherapy with Ifosfamid (Ifo)
def ChemoIfo(rbodysurf, dose, otherCHT):
    ifo = int(dose * rbodysurf)
    mesna = ifo * 0.8
    ifocycle = ifo // 2000
    mesnacycle = ifocycle + 1
    iforemnant = ifo % 2000
    mesnainit = 1200
    mesnaend = 800
    
    if otherCHT:
        st.write(f"Epirubicin 60mg/m2........ {60 * rbodysurf} mg D1, D2")
        st.write(f"Ifosfamid 3000mg/m2.......... {ifo} mg D1,D2,D3")
        st.write(f"Mesna 0.8 x ifosfamid........ {mesna} mg D1,D2,D3")
        st.write("NC 21. deň")
        st.write("D1")
        st.write("Ondasetron 8mg iv, Dexametazon 8mg iv, Pantoprazol 40mg p.o.")
        st.write(f"Epirubicin {60 * rbodysurf} mg v 500ml FR iv")
        st.write(f"MESNA {mesnainit} mg v 100ml FR /4hodiny")
        if iforemnant > 200:
            mesnacont = (mesna - 2000) // ifocycle
            for cycifo in range(0, ifocycle):
                st.write("Ifosfamid 2000mg v 500ml FR iv")
                st.write(f"MESNA {mesnacont} mg v 100ml FR iv/ 4 hodiny")
            st.write(f"Ifosfamid {iforemnant} mg 500ml FR iv")
            st.write("MESNA 800mg v 100ml FR iv/ 4 hodiny")   
        else: 
            mesnacont = (mesna - 1200) // ifocycle
            for cycifo in range(0, ifocycle):
                st.write("Ifosfamid 2000mg v 500ml FR iv")
                st.write(f"MESNA {mesnacont} mg v 100ml FR iv/ 4 hodiny")
    
    else:
        st.write(f"Ifosfamid 3000mg/m2.......... {ifo} mg D1,D2,D3")
        st.write(f"Mesna 0.8 x ifosfamid........ {mesna} mg D1,D2,D3")
        st.write("NC 21. deň")
        st.write("D1")
        st.write("Ondasetron 8mg iv, Dexametazon 8mg iv, Pantoprazol 40mg p.o.")
        st.write(f"MESNA {mesnainit} mg v 100ml FR /4hodiny")
        if iforemnant > 200:
            mesnacont = (mesna - 2000) // ifocycle
            for cycifo in range(0, ifocycle):
                st.write("Ifosfamid 2000mg v 500ml FR iv")
                st.write(f"MESNA {mesnacont} mg v 100ml FR iv/ 4 hodiny")
            st.write(f"Ifosfamid {iforemnant} mg 500ml FR iv")
            st.write("MESNA 800mg v 100ml FR iv/ 4 hodiny")   
        else: 
            mesnacont = (mesna - 1200) // ifocycle
            for cycifo in range(0, ifocycle):
                st.write("Ifosfamid 2000mg v 500ml FR iv")
                st.write(f"MESNA {mesnacont} mg v 100ml FR iv/ 4 hodiny")

# Main function for sarcomas, CNS, and neuroendocrine tumors
def sarcnet(rbodysurf):
    """Táto funkcia rozpisuje chemoterapie a biologickú liečbu sarkómov a CNS a neuroendokrinnych tumorov"""
    chemo_choice = st.selectbox("Vyberte chemoterapiu:", ["Vyberte chemoterapiu", "Ifosfamid/ Epirubicin", "Ifosfamid", "Trabectedin", "Doxorubicin", "Paclitaxel weekly", "CBDCA/ Paclitaxel", "DDP/ Etoposid", "CBDCA/ Etoposid", "Dakarbazin 5 dňový", "Temozolomid", "Lomustine (CCNU)",
        # --- Nové (2026-06) ---
        "CAPTEM (Kapecitabín + Temozolomid, pNET, E2211)",
        "Pazopanib 800 mg/deň (STS, PALETTE)",
    ])

    if chemo_choice == "Ifosfamid/ Epirubicin":
        ChemoIfo(rbodysurf, 3000, True)
    elif chemo_choice == "Ifosfamid":
        ChemoIfo(rbodysurf, 3000, False)
    elif chemo_choice == "Trabectedin":
        Chemo(rbodysurf, "trabectedin.json")
    elif chemo_choice == "Doxorubicin":
        Chemo(rbodysurf, "doxorubicin.json")
    elif chemo_choice == "Paclitaxel weekly":
        Chemo(rbodysurf, "paclitaxelweekly.json")
    elif chemo_choice == "CBDCA/ Paclitaxel":
        ChemoCBDCA(rbodysurf, "paclitaxel3weekly.json")
    elif chemo_choice == "DDP/ Etoposid":
        ChemoDDP(rbodysurf, "etoposide.json")
    elif chemo_choice == "CBDCA/ Etoposid":
        ChemoCBDCA(rbodysurf, "etoposide.json")
    elif chemo_choice == "Dakarbazin 5 dňový":
        Chemo(rbodysurf, "dacarbazine.json")
    elif chemo_choice == "Temozolomid":
        temozolomide_choice = st.selectbox("Temozolomid je:", ["Vyberte možnosť", "v rámci chemoRAT", "solo 150mg/m2", "solo 200mg/m2"])
        if temozolomide_choice == "v rámci chemoRAT":
            Chemo(rbodysurf, "temozolomideRAT.json")
        elif temozolomide_choice == "solo 150mg/m2":
            Chemo(rbodysurf, "temozolomide150.json")
        elif temozolomide_choice == "solo 200mg/m2":
            Chemo(rbodysurf, "temozolomide200.json")
    elif chemo_choice == "Lomustine (CCNU)":
        Chemo(rbodysurf, "CCNU.json")
    elif chemo_choice == "CAPTEM (Kapecitabín + Temozolomid, pNET, E2211)":
        Chemo(rbodysurf, "captem.json")
    elif chemo_choice == "Pazopanib 800 mg/deň (STS, PALETTE)":
        Chemo(rbodysurf, "pazopanib_sts.json")
    elif chemo_choice == "Ifosfamid high-dose 2000 mg/m² D1-5":
        Chemo(rbodysurf, "ifosfamid_high.json")

# Main input function for weight and height
def main():
    st.title("ChemoThon Sarcoma, CNS and NET SK v2.2")
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
        sarcnet(st.session_state.rbodysurf)

if __name__ == "__main__":
    main()



# ===== Zdroje / Sources (pridané 2026-06, aditívne) =====
with st.expander("📚 Zdroje k režimom / Sources"):
    st.markdown("""**Kľúčové referencie – sarkómy, CNS a NET**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-sarcoma-and-gist) · [NCCN](https://www.nccn.org/guidelines/category_1). Vždy overte podľa aktuálnej verzie guidelines a dostupných balení liečiv. Stav: jún 2026.

- **Doxorubicín (1. línia STS)** — Judson et al., Lancet Oncol 2014 (EORTC 62012).
- **Ifosfamid / doxorubicín (epirubicín)** — EORTC 62012 – Judson et al., Lancet Oncol 2014.
- **Ifosfamid (high-dose)** — Záchranná liečba STS – ESMO sarcoma guideline.
- **Trabektedín** — Demetri et al., J Clin Oncol 2016 (liposarkóm/leiomyosarkóm).
- **Paklitaxel weekly (angiosarkóm)** — Penel et al., J Clin Oncol 2008 (ANGIOTAX).
- **CBDCA / paklitaxel** — ESMO – vybrané indikácie.
- **DDP / etopozid; CBDCA / etopozid (NET G3 / SCLC-like)** — Moertel et al.; NORDIC NEC – Sorbye et al., Ann Oncol 2013.
- **Dakarbazín (5-dňový)** — DTIC pri leiomyosarkóme/melanóme – ESMO.
- **Temozolomid** — Stupp et al., NEJM 2005 (gliblastóm, +RT); CAPTEM pri NET.
- **Lomustín (CCNU)** — Rekurentný gliblastóm – Wick et al., NEJM 2017 (kontrolné rameno).

**Aktuálne štandardy na zváženie (zatiaľ mimo nástroja):**
- Capecitabín + temozolomid (CAPTEM) pri pankreatických NET – Kunz et al., J Clin Oncol 2023 (ECOG-ACRIN E2211).""")
