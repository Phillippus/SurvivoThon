import streamlit as st
import json
from chemo_utils import bsa, Chemo, ChemoCBDCA, Chemo5FU, show_evidence

# Function for platinum + 5FU chemotherapy
def platinum5FU(rbodysurf):
    """Táto chemoterapia slúži na rozpis chemoterapie s platinou a 5FU"""
    
    a = 80 * rbodysurf
    b = a // 50
    c = a % 50
    rng = int(b)
    
    # Updated selectbox with no default selection
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
        CrCl = st.number_input("Zadajte hodnotu clearance v ml/min", min_value=1, max_value=250, value=None)
        AUC = st.number_input("Zadajte hodnotu AUC 2-6", min_value=2, max_value=6, value=None)
        
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
        else:
            st.error("Prosím, zadajte platnú hodnotu clearance (CrCl) a AUC pred pokračovaním.")
    else:
        st.warning("Prosím, vyberte platinu pre pokračovanie.")

# Main function for gastrointestinal malignancies
def gastrointestinal(rbodysurf, weight=None):
    """Táto funkcia rozpisuje chemoterapie používané v liečbe gastrointestinálnych malignít"""

    chemo_options = {
        " ": None,
        "Pt/5-FU": platinum5FU,
        "FLOT": "FLOT.json",
        "EOX": "EOX.json",
        "Paclitaxel weekly": "paclitaxelweekly.json",
        "CROSS režim": "paclitaxel50weekly.json",
        "FOLFIRINOX": "FOLFIRINOX.json",
        "Gemcitabin/ Capecitabine": "gemcap.json",
        "Gemcitabin/ Nab-Paclitaxel": "gemnabpcl.json",
        "NALIRI/ 5-FU": "peglipiri5FU.json",
        "NALIRIFOX": "NALIRIFOX.json",
        "Gemcitabin": "gemcitabin4w.json",
        "Mitomycin/ 5-FU": "mtc5FU.json",
        # --- Nové (2026-06) ---
        "Nivolumab 360 mg flat + FOLFOX/CAPOX (gastric, CheckMate-649)": "nivolumab_gastric.json",
        "Trastuzumab-deruxtecan 6.4 mg/kg (HER2+ gastric, DESTINY-Gastric01)": "tdx_gastric.json",
        "Ramucirumab 8 mg/kg q2w (gastric 2. línia, REGARD)": "ramucirumab.json",
        "Ramucirumab + Paclitaxel weekly (gastric 2. línia, RAINBOW)": "ramucirumab_paclitaxel.json",
        # --- Nové 2026-06 doplnené ---
        "Platina + Gemcitabin (žlčové cesty, ABC-02)": "platina_gem_biliary",
        "Platina + Kapecitabín + Trastuzumab (HER2+ gastric, ToGA)": "platina_cape_trastu",
    }

    chemo_choice = st.selectbox("Vyberte chemoterapiu:", list(chemo_options.keys()))

    if chemo_choice and chemo_choice != "Vyberte chemoterapiu":
        if chemo_choice == "Pt/5-FU":
            platinum5FU(rbodysurf)
        elif chemo_choice == "Platina + Gemcitabin (žlčové cesty, ABC-02)":
            pt_biliary = st.selectbox("Ktorá platina?", ["Vyberte", "Cisplatina 25 mg/m2 D1,8", "Karboplatina AUC 5 D1"], key="pt_biliary")
            if pt_biliary == "Cisplatina 25 mg/m2 D1,8":
                ddp_dose = round(25 * rbodysurf, 2)
                gem_dose = round(1000 * rbodysurf, 2)
                st.write(f"### Cisplatina + Gemcitabin (žlčové cesty)")
                st.write(f"cisplatina 25 mg/m2 ......... {ddp_dose} mg D1, D8")
                st.write(f"gemcitabin 1000 mg/m2 ......... {gem_dose} mg D1, D8")
                st.write("NC 21. deň")
                st.write("D1 - premedikácia:")
                import json as _j
                bl = _j.load(open("data/cisplatin_gem_biliary.json", encoding="utf-8"))
                st.write(bl["Day1"]["Premed"]["Note"])
                st.write("D1 - chemoterapia:")
                st.write(f"gemcitabin {gem_dose} mg v 500ml FR i.v./30 min D1")
                ddp_vials = int(ddp_dose // 50); ddp_rem = round(ddp_dose % 50, 2)
                for _ in range(ddp_vials):
                    st.write("cisplatina 50mg v 250ml FR i.v./60 min")
                if ddp_rem > 0:
                    st.write(f"cisplatina {ddp_rem} mg v 250ml FR i.v./60 min")
                st.write("Manitol 10% 250ml i.v. po cisplatine")
                st.write("--- D8 ---")
                st.write(f"gemcitabin {gem_dose} mg v 500ml FR i.v./30 min D8")
                for _ in range(ddp_vials):
                    st.write("cisplatina 50mg v 250ml FR i.v./60 min D8")
                if ddp_rem > 0:
                    st.write(f"cisplatina {ddp_rem} mg v 250ml FR i.v./60 min D8")
            elif pt_biliary == "Karboplatina AUC 5 D1":
                CrCl_b = st.number_input("Clearance (ml/min):", min_value=1, max_value=250, value=None, key="crcl_biliary")
                gem_dose = round(1000 * rbodysurf, 2)
                if CrCl_b is not None:
                    cbdca_dose = (CrCl_b + 25) * 5
                    st.write(f"### Karboplatina + Gemcitabin (žlčové cesty)")
                    st.write(f"karboplatina AUC 5 ......... {cbdca_dose} mg D1")
                    st.write(f"gemcitabin 1000 mg/m2 ......... {gem_dose} mg D1, D8")
                    st.write("NC 21. deň")
                    import json as _j
                    bl = _j.load(open("data/cbdca_gem_biliary.json", encoding="utf-8"))
                    st.write(bl["Day1"]["Premed"]["Note"])
                    st.write(f"karboplatina {cbdca_dose} mg v 500ml FR i.v./60 min D1")
                    st.write(f"gemcitabin {gem_dose} mg v 500ml FR i.v./30 min D1, D8")
        elif chemo_choice == "Platina + Kapecitabín + Trastuzumab (HER2+ gastric, ToGA)":
            pt_her2 = st.selectbox("Ktorá platina?", ["Vyberte", "Cisplatina 80 mg/m2 D1", "Karboplatina AUC 5-6 D1", "Oxaliplatina 130 mg/m2 D1 (switch z DDP)"], key="pt_her2")
            # Výpočet dávky trastuzumabu z hmotnosti (8 mg/kg 1. dávka, 6 mg/kg ďalšie)
            trastu_first = round(8 * weight, 2) if weight else None
            trastu_maint = round(6 * weight, 2) if weight else None

            def trastu_line_listing():
                if weight:
                    st.write(f"trastuzumab 8 mg/kg (1. dávka) ......... {trastu_first} mg / "
                             f"ďalšie 6 mg/kg ......... {trastu_maint} mg D1 q3w")
                else:
                    st.warning("Zadajte hmotnosť pre výpočet dávky trastuzumabu.")
                    st.write("trastuzumab 8 mg/kg (1. dávka) / 6 mg/kg (ďalšie) q3w")

            def trastu_line_admin():
                if weight:
                    st.write(f"trastuzumab {trastu_first} mg (1. dávka) alebo {trastu_maint} mg (ďalšie) "
                             f"v 250ml FR i.v./90 min (1. infúzia), 30 min (ďalšie)")
                else:
                    st.write("trastuzumab 8 mg/kg (1. dávka) alebo 6 mg/kg (ďalšie) "
                             "v 250ml FR i.v./90 min (1. infúzia), 30 min (ďalšie)")

            if pt_her2 == "Cisplatina 80 mg/m2 D1":
                ddp_dose = round(80 * rbodysurf, 2)
                cape_dose = round(1000 * rbodysurf, 2)
                b = ddp_dose // 50; c = ddp_dose % 50; rng = int(b)
                st.write(f"### Cisplatina + Kapecitabín + Trastuzumab (HER2+ gastric)")
                st.write(f"cisplatina 80 mg/m2 ......... {ddp_dose} mg D1")
                st.write(f"kapecitabín 1000 mg/m2 ......... {cape_dose} mg D1-14 (2× denne)")
                trastu_line_listing()
                st.write("NC 21. deň")
                import json as _j
                trastu = _j.load(open("data/ddp_capecitabine_trastu.json", encoding="utf-8"))
                st.write("D1 - premedikácia:")
                st.write(trastu["Day1"]["Premed"]["Note"])
                st.write("D1 - chemoterapia:")
                for ordo in range(1, rng + 1):
                    st.write(f"cisplatina 50mg v 500ml RR i.v.")
                if c > 0:
                    st.write(f"cisplatina {round(c, 2)} mg v 500ml RR i.v.")
                st.write("Manitol 10% 250ml i.v.")
                st.write(f"kapecitabín {cape_dose} mg p.o. 2× denne D1-14")
                trastu_line_admin()
                show_evidence(trastu)
            elif pt_her2 == "Karboplatina AUC 5-6 D1":
                CrCl_h = st.number_input("Clearance (ml/min):", min_value=1, max_value=250, value=None, key="crcl_her2")
                AUC_h = st.number_input("AUC (5 alebo 6):", min_value=4, max_value=6, value=5, key="auc_her2")
                cape_dose = round(1000 * rbodysurf, 2)
                if CrCl_h is not None:
                    cbdca_dose = (CrCl_h + 25) * AUC_h
                    st.write(f"### Karboplatina + Kapecitabín + Trastuzumab (HER2+ gastric)")
                    st.write(f"karboplatina AUC {AUC_h} ......... {cbdca_dose} mg D1")
                    st.write(f"kapecitabín 1000 mg/m2 ......... {cape_dose} mg D1-14 (2× denne)")
                    trastu_line_listing()
                    st.write("NC 21. deň")
                    import json as _j
                    trastu = _j.load(open("data/cbdca_capecitabine_trastu.json", encoding="utf-8"))
                    st.write("D1 - premedikácia:")
                    st.write(trastu["Day1"]["Premed"]["Note"])
                    st.write("D1 - chemoterapia:")
                    st.write(f"karboplatina {cbdca_dose} mg v 500ml FR i.v./60 min D1")
                    st.write(f"kapecitabín {cape_dose} mg p.o. 2× denne D1-14")
                    trastu_line_admin()
                    show_evidence(trastu)
            elif pt_her2 == "Oxaliplatina 130 mg/m2 D1 (switch z DDP)":
                oxa_dose = round(130 * rbodysurf, 2)
                cape_dose = round(1000 * rbodysurf, 2)
                st.write(f"### Oxaliplatina + Kapecitabín + Trastuzumab (SWITCH z cisplatiny)")
                st.write(f"oxaliplatina 130 mg/m2 ......... {oxa_dose} mg D1")
                st.write(f"kapecitabín 1000 mg/m2 ......... {cape_dose} mg D1-14 (2× denne)")
                if weight:
                    st.write(f"trastuzumab pokračuje 6 mg/kg ......... {trastu_maint} mg D1 q3w")
                else:
                    st.warning("Zadajte hmotnosť pre výpočet dávky trastuzumabu.")
                    st.write("trastuzumab pokračuje 6 mg/kg q3w")
                st.write("NC 21. deň")
                import json as _j
                trastu = _j.load(open("data/oxa_capecitabine_trastu.json", encoding="utf-8"))
                st.write("D1 - premedikácia:")
                st.write(trastu["Day1"]["Premed"]["Note"])
                st.write("D1 - chemoterapia:")
                st.write(f"oxaliplatina {oxa_dose} mg v 250ml 5%GLC i.v./120 min D1")
                st.write(f"kapecitabín {cape_dose} mg p.o. 2× denne D1-14")
                if weight:
                    st.write(f"trastuzumab {trastu_maint} mg v 250ml FR i.v./30 min (udržiavacia dávka)")
                else:
                    st.write("trastuzumab 6 mg/kg v 250ml FR i.v./30 min (udržiavacia dávka)")
                show_evidence(trastu)
                st.write("trastuzumab 6 mg/kg v 250ml FR i.v./30 min (switch z DDP)")
        else:
            chemo_file = chemo_options[chemo_choice]
            if chemo_choice in ["FLOT", "FOLFIRINOX", "NALIRI/ 5-FU", "NALIRIFOX", "Mitomycin/ 5-FU"]:
                Chemo5FU(rbodysurf, chemo_file)
            elif chemo_choice in ["CROSS režim"]:
                ChemoCBDCA(rbodysurf, chemo_file)
            else:
                Chemo(rbodysurf, chemo_file, weight=weight)

# Main input function for weight and height
def main():
    st.title("ChemoThon - GastrointestinalSK (excl. CrC) v2.2")
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
        st.session_state.weight = weight
        st.session_state.show_chemo_selection = True

    # Display the BSA if it's already calculated, and only once
    if 'rbodysurf' in st.session_state:
        st.write(f"Telesný povrch je: {st.session_state.rbodysurf} m²")

    # Step 2: Chemotherapy selection if BSA is calculated
    if st.session_state.get("show_chemo_selection", False):
        st.write("Teraz vyberte chemoterapiu:")
        gastrointestinal(st.session_state.rbodysurf, st.session_state.get('weight'))

if __name__ == "__main__":
    main()
       



# ===== Zdroje / Sources (pridané 2026-06, aditívne) =====
with st.expander("📚 Zdroje k režimom / Sources"):
    st.markdown("""**Kľúčové referencie – GI nádory (mimo CRC)**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-gastrointestinal-cancers) · [NCCN](https://www.nccn.org/guidelines/category_1). Vždy overte podľa aktuálnej verzie guidelines a dostupných balení liečiv. Stav: jún 2026.

- **FLOT (perioperačne)** — FLOT4 – Al-Batran et al., Lancet 2019.
- **EOX / ECX** — REAL-2 – Cunningham et al., NEJM 2008.
- **Paklitaxel weekly (gastrický, 2. línia)** — +ramucirumab RAINBOW – Wilke et al., Lancet Oncol 2014.
- **CROSS (karboplatina/paklitaxel + RT)** — van Hagen et al., NEJM 2012 (CROSS).
- **FOLFIRINOX (pankreas)** — Conroy et al., NEJM 2011 (PRODIGE 4/ACCORD 11).
- **Gemcitabín / kapecitabín** — Cunningham et al., J Clin Oncol 2009.
- **Gemcitabín / nab-paklitaxel** — MPACT – Von Hoff et al., NEJM 2013.
- **NALIRI / 5-FU (lipozomálny irinotekan)** — NAPOLI-1 – Wang-Gillam et al., Lancet 2016.
- **NALIRIFOX** — NAPOLI-3 – Wainberg et al., Lancet 2023.
- **Gemcitabín (monoterapia)** — Burris et al., J Clin Oncol 1997.
- **Mitomycín / 5-FU (anál)** — Nigro / RTOG 98-11 – Ajani et al., JAMA 2008.

**Aktuálne štandardy na zváženie (zatiaľ mimo nástroja):**
- **Nivolumab + chemoterapia (CPS≥5) – CheckMate-649, Lancet 2021 → teraz v nástroji.**
- Pembrolizumab + trastuzumab + chemo pri HER2+ gastrickom – KEYNOTE-811, Nature 2024.
- **T-DXd 6.4 mg/kg gastric – DESTINY-Gastric01, NEJM 2020 → teraz v nástroji.**
- Zolbetuximab + chemo pri CLDN18.2+ – SPOTLIGHT/GLOW, Lancet 2023.""")
