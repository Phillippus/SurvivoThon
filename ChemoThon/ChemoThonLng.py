import streamlit as st
import json
import chemo_utils as _cu, importlib as _il
_il.reload(_cu)  # deploy-safe: vynúti čerstvý chemo_utils (Streamlit cachuje moduly)
from chemo_utils import bsa, Chemo, ChemoCBDCA, ChemoDDP, show_evidence

def lung(rbodysurf):
    """Tato funkcia ponuka chemoterapie pouzivane v liecbe karcinomu pluc"""
    chemo_options = [
        "Vyberte chemoterapiu",
        "CBDCA + paclitaxel",
        "CBDCA + pemetrexed",
        "DDP + gemcitabine",
        "CBDCA + gemcitabine",
        "DDP + etoposide",
        "Topotecan + G-CSF",
        # --- Nové (2026-06) ---
        "Pembrolizumab + Pemetrexed + CBDCA (neskvamózny NSCLC, KEYNOTE-189)",
        "Pembrolizumab + CBDCA + Nab-Paclitaxel (skvamózny NSCLC, KEYNOTE-407)",
        "Durvalumab 1500 mg flat q4w (PACIFIC, udržiavanie po CRT štádium III)",
        "Atezolizumab + Etoposid + CBDCA (SCLC 1. línia, IMpower133)",
        # --- Nové 2026-06 doplnené ---
        "Platina + Vinorelbin (adjuvantná, IALT/ANITA)",
    ]
    lng = st.selectbox("Vyberte chemoterapiu, ktorú chcete podať:", chemo_options)

    if lng != chemo_options[0]:  # Ensure that the default "Vyberte chemoterapiu" is not selected
        if lng == "CBDCA + paclitaxel":
            ChemoCBDCA(rbodysurf, "paclitaxel3weekly.json")
        elif lng == "CBDCA + pemetrexed":
            ChemoCBDCA(rbodysurf, "pemetrexed.json")
        elif lng == "DDP + gemcitabine":
            ChemoDDP(rbodysurf, "gemcitabinDDP.json")
        elif lng == "CBDCA + gemcitabine":
            ChemoCBDCA(rbodysurf, "gemcitabinCBDCA.json")
        elif lng == "DDP + etoposide":
            ChemoDDP(rbodysurf, "etoposide.json")
        elif lng == "Topotecan + G-CSF":
            Chemo(rbodysurf, "topotecan.json")
        elif lng == "Pembrolizumab + Pemetrexed + CBDCA (neskvamózny NSCLC, KEYNOTE-189)":
            ChemoCBDCA(rbodysurf, "pembrolizumab_pem_cbdca.json")
        elif lng == "Pembrolizumab + CBDCA + Nab-Paclitaxel (skvamózny NSCLC, KEYNOTE-407)":
            ChemoCBDCA(rbodysurf, "pembrolizumab_cbdca_nab.json")
        elif lng == "Durvalumab 1500 mg flat q4w (PACIFIC, udržiavanie po CRT štádium III)":
            Chemo(rbodysurf, "durvalumab_pacific.json")
        elif lng == "Platina + Vinorelbin (adjuvantná, IALT/ANITA)":
            pt_adj = st.selectbox("Ktorá platina?", ["Vyberte", "Cisplatina 75-80 mg/m2 D1 (IALT/ANITA)", "Karboplatina AUC 5-6 D1 (alternatíva)"], key="pt_adj_vin")
            if pt_adj == "Cisplatina 75-80 mg/m2 D1 (IALT/ANITA)":
                vin_dose = round(25 * rbodysurf, 2)
                a = round(80 * rbodysurf, 2); b = int(a // 50); c = a % 50
                st.write(f"### DDP + Vinorelbin (adjuvantná NSCLC)")
                st.write(f"cisplatina 80 mg/m2 ......... {a} mg D1")
                st.write(f"vinorelbin 25 mg/m2 ......... {vin_dose} mg D1, D8")
                st.write("NC 28. deň")
                import json as _j
                vn = _j.load(open("data/vinorelbine_ddp_adj.json", encoding="utf-8"))
                st.write(vn["Day1"]["Premed"]["Note"])
                for i in range(b):
                    st.write(f"cisplatina 50mg v 500ml RR i.v.")
                if c > 0:
                    st.write(f"cisplatina {round(c, 2)} mg v 500ml RR i.v.")
                st.write("Manitol 10% 250ml i.v.")
                st.write(f"vinorelbin {vin_dose} mg v 125ml FR i.v./10 min D1, D8")
                show_evidence(vn)
            elif pt_adj == "Karboplatina AUC 5-6 D1 (alternatíva)":
                CrCl_a = st.number_input("Clearance (ml/min):", min_value=1, max_value=250, value=None, key="crcl_adj")
                AUC_a = st.number_input("AUC (5 alebo 6):", min_value=4, max_value=6, value=5, key="auc_adj")
                vin_dose = round(25 * rbodysurf, 2)
                if CrCl_a is not None:
                    cbdca_dose = (CrCl_a + 25) * AUC_a
                    st.write(f"### CBDCA + Vinorelbin (adjuvantná NSCLC)")
                    st.write(f"karboplatina AUC {AUC_a} ......... {cbdca_dose} mg D1")
                    st.write(f"vinorelbin 25 mg/m2 ......... {vin_dose} mg D1, D8")
                    st.write("NC 28. deň")
                    import json as _j
                    vn = _j.load(open("data/vinorelbine_cbdca_adj.json", encoding="utf-8"))
                    st.write(vn["Day1"]["Premed"]["Note"])
                    st.write(f"karboplatina {cbdca_dose} mg v 500ml FR i.v./60 min")
                    st.write(f"vinorelbin {vin_dose} mg v 125ml FR i.v./10 min D1, D8")
                    show_evidence(vn)
        elif lng == "Atezolizumab + Etoposid + CBDCA (SCLC 1. línia, IMpower133)":
            ChemoCBDCA(rbodysurf, "atezolizumab_ep.json")

def main():
    st.title("          ChemoThon- LungSK v 2.3")
    st.write("""
    Program rozpisuje najbežnejšie chemoterapie podľa povrchu alebo hmotnosti.
    Dávky je nutné upraviť podľa aktuálne dostupných balení liečiv.
    Autor nezodpovedá za prípadné škody spôsobené jeho použitím!
    Pripomienky posielajte na filip.kohutek@fntn.sk
    Program kedykoľvek ukončíte zatvorením okna.
    """)

    # Step 1: Input weight and height
    w = st.number_input("Zadajte hmotnosť (kg):", min_value=1, max_value=250, value=70)
    h = st.number_input("Zadajte výšku (cm):", min_value=1, max_value=250, value=170)

    if st.button("Vypočítať telesný povrch"):
        rbodysurf = bsa(w, h)
        st.session_state.rbodysurf = rbodysurf
        st.session_state.show_chemo = True

    if "rbodysurf" in st.session_state:
        st.write(f"Telesný povrch je: {st.session_state.rbodysurf} m²")

    # Step 2: Select chemotherapy
    if st.session_state.get("show_chemo", False):
        lung(st.session_state.rbodysurf)

if __name__ == "__main__":
    main()



# ===== Zdroje / Sources (pridané 2026-06, aditívne) =====
with st.expander("📚 Zdroje k režimom / Sources"):
    st.markdown("""**Kľúčové referencie – nádory pľúc**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-lung-and-chest-tumours) · [NCCN](https://www.nccn.org/guidelines/category_1). Vždy overte podľa aktuálnej verzie guidelines a dostupných balení liečiv. Stav: jún 2026.

- **CBDCA / paklitaxel** — ECOG 1594 – Schiller et al., NEJM 2002.
- **Cisplatina / pemetrexed (neskvamózny)** — Scagliotti et al., J Clin Oncol 2008.
- **Gemcitabín / cisplatina** — ECOG 1594; štandardná platina-dubleta.
- **Gemcitabín / karboplatina** — Platina-dubleta pri NSCLC – NCCN NSCLC.
- **Etopozid / platina (SCLC)** — Štandard pre SCLC; + atezolizumab IMpower133, NEJM 2018.
- **Topotekan (SCLC, 2. línia)** — O'Brien et al., J Clin Oncol 2006.

**Aktuálne štandardy na zváženie (zatiaľ mimo nástroja):**
- Pridanie PD-(L)1 inhibítora k chemoterapii v 1. línii (KEYNOTE-189/407, IMpower).
- Pri EGFR/ALK/ROS1 a iných cieľoch – cielená liečba pred chemoterapiou (osimertinib, alektinib...).""")
