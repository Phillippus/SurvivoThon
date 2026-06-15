import streamlit as st
import json
import chemo_utils as _cu, importlib as _il
_il.reload(_cu)  # deploy-safe: vynúti čerstvý chemo_utils (Streamlit cachuje moduly)
from chemo_utils import bsa, Chemo, ChemoCBDCA, show_evidence

# Function for chemotherapy with Cisplatin
def ChemoCISplatin(rbodysurf, chemoType):
    """Táto funkcia slúži pre rozpis chemoterapie s cisplatinou a paclitaxelom"""
    with open('data/' + chemoType, "r") as chemoFile:
        chemoJson = json.loads(chemoFile.read())

    cisplatin_dose = round(80 * rbodysurf, 2)
    st.write(f"Cisplatina 80 mg/m² ........ {cisplatin_dose} mg D1")
    for i in chemoJson["Chemo"]:
        st.write(f"{i['Name']} {i['Dosage']} {i['DosageMetric']} ..... {round(i['Dosage'] * rbodysurf, 2)} mg D{i['Day']}")

    st.write(f"NC {chemoJson['NC']} . deň")

    st.write("D1 - premedikácia:")
    st.write(chemoJson["Day1"]["Premed"]["Note"])

    st.write("D1 - chemoterapia:")

    # Výpis dávok paclitaxelu
    for x in range(len(chemoJson["Chemo"])):
        st.write(f"{chemoJson['Day1']['Instructions'][x]['Name']} {round(chemoJson['Chemo'][x]['Dosage'] * rbodysurf, 2)} mg {chemoJson['Day1']['Instructions'][x]['Inst']}")

    # Výpis cisplatiny po 50 mg
    remaining = cisplatin_dose
    while remaining > 0:
        part = 50 if remaining >= 50 else round(remaining, 2)
        st.write(f"cisplatina {part} mg v 500 ml Ringerovho roztoku (RR)")
        remaining -= part
    st.write("po dotečení cisplatiny Manitol 10% 250ml iv")

# Function for chemotherapy based on weight (e.g. bevacizumab)
def ChemoWeightBased(weight, chemoType):
    """Táto funkcia rozpisuje chemoterapiu podľa hmotnosti (napr. bevacizumab)"""
    with open('data/' + chemoType, "r") as chemoFile:
        chemoJson = json.loads(chemoFile.read())

    st.write("Rozpis chemoterapie:")
    for i in chemoJson["Chemo"]:
        dose = round(i["Dosage"] * weight, 2)
        st.write(f"{i['Name']} {i['Dosage']} {i['DosageMetric']} .......... {dose} mg D{i['Day']}")

    st.write(f"NC {chemoJson['NC']} . deň")

    st.write("D1 - premedikácia:")
    st.write(chemoJson["Day1"]["Premed"]["Note"] or "žiadna premedikácia")

    st.write("D1 - chemoterapia:")
    for x in range(len(chemoJson["Chemo"])):
        dose = round(chemoJson["Chemo"][x]["Dosage"] * weight, 2)
        st.write(f"{chemoJson['Day1']['Instructions'][x]['Name']} {dose} mg {chemoJson['Day1']['Instructions'][x]['Inst']}")

    show_evidence(chemoJson)

# Main function for gynecology chemotherapy
def gynecology(rbodysurf):
    """Táto funkcia rozpisuje chemoterapie gynekologických tumorov"""
    chemo_choice = st.selectbox("Akú chemoterapiu chcete podať?", [
        "  ",
        "CBDCA/ paclitaxel",
        "INTERLACE CBDCA/paclitaxel (6 cyklov → konkomitantná RT)",
        "Cisplatina/ paclitaxel",
        "Topotecan + G-CSF",
        "PEG-doxorubicin",
        "CBDCA/ PEG-doxorubicin",
        "CBDCA/ gemcitabin",
        "Bevacizumab 15 mg/kg",
        # --- Nové (2026-06) ---
        "Mirvetuximab soravtansín 6 mg/kg (PROC FRα+, MIRASOL)",
        "Lenvatinib 20 mg/deň + Pembrolizumab (endometrium, KEYNOTE-775)",
        "Pembrolizumab + CBDCA + Paclitaxel (endometrium, NRG-GY018)",
        "Platina + Paklitaxel + Bevacizumab + Pembrolizumab (endometrium/cervix)",
    ])

    if chemo_choice == "CBDCA/ paclitaxel":
        ChemoCBDCA(rbodysurf, "paclitaxel3weekly.json")
    elif chemo_choice == "INTERLACE CBDCA/paclitaxel (6 cyklov → konkomitantná RT)":
        st.info("⚠️ INTERLACE: 6 cyklov indukčnej CBDCA/paklitaxel (AUC 2 / 80 mg/m²), potom prechod na cisplatinu 40 mg/m² weekly počas rádioterapie (alternatíva: flat dose cisplatina 50 mg weekly).")
        ChemoCBDCA(rbodysurf, "paclitaxelweekly.json")
    elif chemo_choice == "Cisplatina/ paclitaxel":
        ChemoCISplatin(rbodysurf, "paclitaxel3weeklyDDP.json")
    elif chemo_choice == "Topotecan + G-CSF":
        Chemo(rbodysurf, "topotecan.json")
    elif chemo_choice == "PEG-doxorubicin":
        Chemo(rbodysurf, "pegdoxo.json")
    elif chemo_choice == "CBDCA/ PEG-doxorubicin":
        ChemoCBDCA(rbodysurf, "PEGdoxo30.json")
    elif chemo_choice == "CBDCA/ gemcitabin":
        ChemoCBDCA(rbodysurf, "gemcitabinCBDCA.json")
    elif chemo_choice == "Bevacizumab 15 mg/kg":
        if 'weight' in st.session_state:
            ChemoWeightBased(st.session_state.weight, "bevacizumab3w15.json")
        else:
            st.error("Najprv zadajte hmotnosť a výšku a stlačte tlačidlo na výpočet telesného povrchu.")
    elif chemo_choice == "Mirvetuximab soravtansín 6 mg/kg (PROC FRα+, MIRASOL)":
        if 'weight' in st.session_state:
            ChemoWeightBased(st.session_state.weight, "mirvetuximab.json")
        else:
            st.error("Najprv zadajte hmotnosť a výšku.")
    elif chemo_choice == "Lenvatinib 20 mg/deň + Pembrolizumab (endometrium, KEYNOTE-775)":
        Chemo(rbodysurf, "lenvatinib.json")
        st.write("---")
        st.write("**Pembrolizumab (súbežne s lenvatinibom):**")
        st.write("pembrolizumab 200 mg flat dose v 100ml FR i.v./30 min  D1 q3w")
        st.write("NC 21. deň (pembrolizumab q3w, lenvatinib kontinuálne D1-28)")
    elif chemo_choice == "Pembrolizumab + CBDCA + Paclitaxel (endometrium, NRG-GY018)":
        ChemoCBDCA(rbodysurf, "pembrolizumab_carboplatin_paclitaxel_gyn.json")
    elif chemo_choice == "Platina + Paklitaxel + Bevacizumab + Pembrolizumab (endometrium/cervix)":
        import json as _j
        _bpj = _j.load(open("data/cbdca_taxol_beva_pembro_gyn.json", encoding="utf-8"))
        weight = st.session_state.get('weight', None)
        taxol_dose = round(175 * rbodysurf, 2)
        beva_dose = round(15 * weight, 2) if weight else "?"
        pt_choice = st.selectbox("Ktorá platina?", ["Vyberte", "Karboplatina AUC 5 D1", "Cisplatina 50 mg/m2 D1"], key="pt_bpj")
        if pt_choice == "Karboplatina AUC 5 D1":
            CrCl_b = st.number_input("Clearance (ml/min):", min_value=1, max_value=250, value=None, key="crcl_bpj")
            if CrCl_b is not None:
                cbdca_dose = (CrCl_b + 25) * 5
                st.write(f"### Platina + Paklitaxel + Bevacizumab + Pembrolizumab")
                st.write(f"pembrolizumab 200 mg flat dose  D1")
                st.write(f"paklitaxel 175 mg/m2 ......... {taxol_dose} mg D1")
                st.write(f"karboplatina AUC 5 ......... {cbdca_dose} mg D1")
                st.write(f"bevacizumab 15 mg/kg ......... {beva_dose} mg D1")
                st.write(f"NC 21. deň")
                st.write("D1 - premedikácia:")
                st.write(_bpj["Day1"]["Premed"]["Note"])
                st.write("D1 - chemoterapia:")
                st.write(f"pembrolizumab 200 mg {_bpj['Day1']['Instructions'][0]['Inst']}")
                st.write(f"paklitaxel {taxol_dose} mg {_bpj['Day1']['Instructions'][1]['Inst']}")
                st.write(f"karboplatina {cbdca_dose} mg v 500ml FR i.v./60 min")
                st.write(f"bevacizumab {beva_dose} mg {_bpj['Day1']['Instructions'][2]['Inst']}")
                show_evidence(_bpj)
        elif pt_choice == "Cisplatina 50 mg/m2 D1":
            ddp_dose = round(50 * rbodysurf, 2)
            ddp_vials = int(ddp_dose // 50); ddp_rem = round(ddp_dose % 50, 2)
            st.write(f"### Platina + Paklitaxel + Bevacizumab + Pembrolizumab")
            st.write(f"pembrolizumab 200 mg flat dose  D1")
            st.write(f"paklitaxel 175 mg/m2 ......... {taxol_dose} mg D1")
            st.write(f"cisplatina 50 mg/m2 ......... {ddp_dose} mg D1")
            st.write(f"bevacizumab 15 mg/kg ......... {beva_dose} mg D1")
            st.write(f"NC 21. deň")
            st.write("D1 - premedikácia:")
            st.write(_bpj["Day1"]["Premed"]["Note"])
            st.write("D1 - chemoterapia:")
            st.write(f"pembrolizumab 200 mg {_bpj['Day1']['Instructions'][0]['Inst']}")
            st.write(f"paklitaxel {taxol_dose} mg {_bpj['Day1']['Instructions'][1]['Inst']}")
            for _ in range(ddp_vials):
                st.write("cisplatina 50 mg v 500ml RR i.v./60 min")
            if ddp_rem > 0:
                st.write(f"cisplatina {ddp_rem} mg v 500ml RR i.v./60 min")
            st.write("Manitol 10% 250ml i.v. po cisplatine")
            st.write(f"bevacizumab {beva_dose} mg {_bpj['Day1']['Instructions'][2]['Inst']}")
            show_evidence(_bpj)

# Main input function for weight and height
def main():
    st.title("        ChemoThon Gynecology v2.2")
    st.write("""
    Program rozpisuje najbežnejšie chemoterapie podľa povrchu alebo hmotnosti.
    Dávky je nutné upraviť podľa aktuálne dostupných balení liečiv.
    Autor nezodpovedá za prípadné škody spôsobené jeho použitím! 
    Pre podanie/ pridanie imunoterapie prejdite na https://immunothon.streamlit.app.
    Pripomienky posielajte na filip.kohutek@fntn.sk
    Program kedykoľvek ukončíte zatvorením okna.
    """)

    # Step 1: Input weight and height
    weight = st.number_input("Zadajte hmotnosť (kg):", min_value=1, max_value=250, value=None)
    height = st.number_input("Zadajte výšku (cm):", min_value=1, max_value=250, value=None)

    if st.button("Vypočítať telesný povrch") and weight is not None and height is not None:
        rbodysurf = bsa(weight, height)
        st.session_state.rbodysurf = rbodysurf
        st.session_state.weight = weight  # for kg-based regimens like bevacizumab

    # Always display the BSA if it has been calculated
    if 'rbodysurf' in st.session_state:
        st.write(f"Telesný povrch je: {st.session_state.rbodysurf} m²")

    # Step 2: Display chemotherapy options if BSA is calculated
    if 'rbodysurf' in st.session_state:
        st.write("Teraz vyberte chemoterapiu:")
        gynecology(st.session_state.rbodysurf)

if __name__ == "__main__":
    main()



# ===== Zdroje / Sources (pridané 2026-06, aditívne) =====
with st.expander("📚 Zdroje k režimom / Sources"):
    st.markdown("""**Kľúčové referencie – gynekologické nádory**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-gynaecological-cancers) · [NCCN](https://www.nccn.org/guidelines/category_1). Vždy overte podľa aktuálnej verzie guidelines a dostupných balení liečiv. Stav: jún 2026.

- **CBDCA / paklitaxel** — GOG-158 – Ozols et al., J Clin Oncol 2003; ICON3.
- **INTERLACE (indukčná CBDCA/paklitaxel, cervix)** — INTERLACE – McCormack et al., Lancet 2024.
- **Cisplatina / paklitaxel (cervix)** — GOG-240 – Tewari et al., NEJM 2014 (so/bez bevacizumabu).
- **Topotekan + G-CSF** — Topotekan pri relapse ovaria – ten Bokkel Huinink et al., J Clin Oncol 1997.
- **PEG-doxorubicín** — PLD pri rekurentnom ovariu – Gordon et al., J Clin Oncol 2001.
- **CBDCA / PEG-doxorubicín** — CALYPSO – Pujade-Lauraine et al., J Clin Oncol 2010.
- **CBDCA / gemcitabín** — Pfisterer et al., J Clin Oncol 2006 (AGO-OVAR/ICON4-like).
- **Bevacizumab 15 mg/kg** — GOG-218 – Burger et al., NEJM 2011; ICON7 – Perren et al., NEJM 2011.

**Aktuálne štandardy na zváženie (zatiaľ mimo nástroja):**
- PARP inhibítory v udržiavaní (olaparib SOLO-1; niraparib PRIMA) – NEJM 2018/2019.
- Dostarlimab / pembrolizumab + chemo pri endometriálnom karcinóme – RUBY / NRG-GY018, NEJM 2023.
- Mirvetuximab soravtansin pri FRα+ platina-rezistentnom ovariu – MIRASOL, NEJM 2023.""")
