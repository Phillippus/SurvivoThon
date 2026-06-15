import streamlit as st
import json
import chemo_utils as _cu, importlib as _il
_il.reload(_cu)  # deploy-safe: vynúti čerstvý chemo_utils (Streamlit cachuje moduly)
from chemo_utils import bsa as calculate_bsa, load_json, show_evidence

def display_chemotherapy_details(rbodysurf, filename):
    """ Zobrazuje podrobné informácie o chemoterapeutickom režime s využitím telesného povrchu. """
    weight = st.session_state.get('weight_kg', None)
    chemo_json = load_json(filename)
    if chemo_json:
        regimen_name = filename.replace('.json', '')
        st.write(f"### Protokol {regimen_name}")
        for chemo in chemo_json['Chemo']:
            metric = chemo.get('DosageMetric', 'mg/m2')
            if 'flat' in metric.lower():
                st.write(f"{chemo['Name']} {chemo['Dosage']} {metric} D {chemo['Day']}")
            elif 'mg/kg' in metric:
                if weight:
                    dosage = round(chemo['Dosage'] * weight, 2)
                    st.write(f"{chemo['Name']} {chemo['Dosage']} {metric} ......... {dosage} mg D {chemo['Day']}")
                else:
                    st.write(f"{chemo['Name']} {chemo['Dosage']} {metric} ......... (zadajte hmotnosť) D {chemo['Day']}")
            else:
                dosage = round(chemo['Dosage'] * rbodysurf, 2)
                st.write(f"{chemo['Name']} {chemo['Dosage']} {metric} ......... {dosage} mg D {chemo['Day']}")

        st.write(f"                       NC {chemo_json.get('NC', 'Nie je určené')} . deň")
        st.write(" ")
        st.write("                                     D1")
        st.write(chemo_json['Day1']['Premed']['Note'])
        for instruction in chemo_json['Day1']['Instructions']:
            drug_name = instruction['Name']
            item = next((i for i in chemo_json['Chemo'] if i['Name'] == drug_name), None)
            if item:
                metric = item.get('DosageMetric', 'mg/m2')
                if 'flat' in metric.lower():
                    st.write(f"{drug_name} {item['Dosage']} mg {instruction['Inst']}")
                elif 'mg/kg' in metric:
                    if weight:
                        adjusted = round(item['Dosage'] * weight, 2)
                        st.write(f"{drug_name} {adjusted} mg {instruction['Inst']}")
                    else:
                        st.write(f"{drug_name} {item['Dosage']} mg/kg {instruction['Inst']}")
                else:
                    adjusted_dosage = round(item['Dosage'] * rbodysurf, 2)
                    st.write(f"{drug_name} {adjusted_dosage} mg {instruction['Inst']}")

        show_evidence(chemo_json)


def Flatdoser(rbodysurf, chemoType, chemoFlat):
    """ Funkcia pre chemoterapeutické režimy s flat-dose zložkou. """
    chemo_json = load_json(chemoType)
    chemo_json2 = load_json(chemoFlat)

    if chemo_json and chemo_json2:
        regimen_name = chemoType.replace('.json', '')
        st.write(f"### Protokol {regimen_name}")

        for chemo in chemo_json['Chemo']:
            dosage = round(chemo['Dosage'] * rbodysurf, 2)
            st.write(f"{chemo['Name']} {chemo['Dosage']} mg/m2 ......... {dosage} mg D {chemo['Day']}")

        for chemo in chemo_json2['Chemo']:
            metric2 = chemo.get('DosageMetric', 'mg/m2')
            if 'mg/m2' in metric2 and 'max' in metric2.lower():
                # Vincristine cap: calculate BSA-based dose, cap at 2mg
                raw = round(chemo['Dosage'] * rbodysurf, 2)
                capped = min(raw, 2.0)
                st.write(f"{chemo['Name']} {chemo['Dosage']} {metric2} ......... {capped} mg D {chemo['Day']} (BSA: {raw} mg → cappované na max 2 mg)")
            else:
                st.write(f"{chemo['Name']} {metric2} ......... {chemo['Dosage']} mg D {chemo['Day']}")

        st.write(f"                       NC {chemo_json.get('NC', 'Nie je určené')} . deň")

        st.write(" ")
        st.write("                                     D1")
        st.write(chemo_json['Day1']['Premed']['Note'])

        for instruction in chemo_json['Day1']['Instructions']:
            drug_name = instruction['Name']
            dosage = next((item['Dosage'] for item in chemo_json['Chemo'] if item['Name'] == drug_name), None)
            if dosage:
                adjusted_dosage = round(dosage * rbodysurf, 2)
                st.write(f"{drug_name} {adjusted_dosage} mg {instruction['Inst']}")

        for instruction in chemo_json2['Day1']['Instructions']:
            item2 = next((i for i in chemo_json2['Chemo'] if i['Name'] == instruction['Name']), None)
            if item2:
                metric2 = item2.get('DosageMetric', 'mg/m2')
                if 'mg/m2' in metric2 and 'max' in metric2.lower():
                    raw = round(item2['Dosage'] * rbodysurf, 2)
                    capped = min(raw, 2.0)
                    st.write(f"{instruction['Name']} {capped} mg {instruction['Inst']}")
                else:
                    st.write(f"{instruction['Name']} {item2['Dosage']} mg {instruction['Inst']}")

        show_evidence(chemo_json)

def DHAP(rbodysurf):
    """ DHAP: cisplatina + cytarabín + dexametazón """
    DDP = round(rbodysurf * 100, 2)
    cycle = int(DDP // 50)
    remnant = round(DDP % 50, 2)

    st.write(f"cisplatina 100mg/m2........ {DDP} mg D1")
    st.write(f"cytarabin 2000mg/m2 BID....... {round(2000 * rbodysurf, 2)} mg každých 12 hodín D2")
    st.write("dexametazon 40mg .................... 40mg D1-D4")
    st.write("                                        NC 21. deň")
    st.write(" ")
    st.write("                                            D1")
    st.write("1. Palonosetron 0.5mg/Netupitant 300mg (Akynzeo) p.o. 1h pred chemo, Dexametazón 12mg i.v., Pantoprazol 40mg p.o.")

    ordo = 1
    for ordo in range(2, cycle + 2):
        st.write(f"{ordo}. cisplatina 50mg v 500ml RR iv")

    if remnant > 0:
        ordo += 1
        st.write(f"{ordo}. cisplatina {round(remnant, 2)} mg v 500ml RR iv")
        st.write(f"{ordo + 1}. manitol 10% 250ml iv")
        st.write(f"{ordo + 2}. dexametazon 40mg tbl p.o. (+ pantoprazol 40mg p.o.)")
    else:
        st.write(f"{ordo + 1}. manitol 10% 250ml iv")
        st.write(f"{ordo + 2}. dexametazon 40mg tbl p.o. (+ pantoprazol 40mg p.o.)")

def RDHAP(rbodysurf):
    """ R-DHAP: rituximab + cisplatina + cytarabín + dexametazón """
    ritux = round(375 * rbodysurf, 2)
    DDP = round(rbodysurf * 100, 2)
    cycle = int(DDP // 50)
    remnant = round(DDP % 50, 2)

    st.write(f"rituximab 375mg/m2......... {ritux} mg D1")
    st.write(f"cisplatina 100mg/m2........ {DDP} mg D1")
    st.write(f"cytarabin 2000mg/m2 BID....... {round(2000 * rbodysurf, 2)} mg každých 12 hodín D2")
    st.write("dexametazon 40mg .................... 40mg D1-D4")
    st.write("                                        NC 21. deň")
    st.write(" ")
    st.write("                                            D1")
    st.write("1. Hydrocortison 100mg iv, Dithiaden 1amp iv, Pantoprazol 40mg p.o., Palonosetron 0.5mg/Netupitant 300mg (Akynzeo) p.o. 1h pred chemo, Dexametazón 12mg i.v.")
    st.write(f"2. rituximab {ritux} mg v 500ml FR iv/ 1.infuzia: zacat 50ml/h, stupnovite zvysovat; dalsie cykly: 100ml/h")

    ordo = 2
    for ordo in range(3, cycle + 3):
        st.write(f"{ordo}. cisplatina 50mg v 500ml RR iv")

    if remnant > 0:
        ordo += 1
        st.write(f"{ordo}. cisplatina {round(remnant, 2)} mg v 500ml RR iv")
        st.write(f"{ordo + 1}. manitol 10% 250ml iv")
        st.write(f"{ordo + 2}. dexametazon 40mg tbl p.o. (+ pantoprazol 40mg p.o.)")
    else:
        st.write(f"{ordo + 1}. manitol 10% 250ml iv")
        st.write(f"{ordo + 2}. dexametazon 40mg tbl p.o. (+ pantoprazol 40mg p.o.)")

def DA_EPOCH(rbodysurf, with_rituximab=False, dose_level=1):
    """ (DA-)EPOCH(-R): dose-adjusted EPOCH ± rituximab.
    Etoposid, doxorubicin a vinkristín idú ako 96h kontinuálna infúzia D1-4.
    dose_level upravuje etopozid/doxorubicin/cyklofosfamid faktorom 1.2^(level-1)
    (Wilson protokol; eviQ: 750→900→1080…). Vinkristín a prednizón sú fixné. """
    name = "DA-EPOCH-R" if with_rituximab else "DA-EPOCH"
    factor = round(1.2 ** (dose_level - 1), 4)
    st.write(f"### Protokol {name} — dose level {dose_level} ({int(round(factor*100))} % baseline)")

    # Etopozid/doxorubicin/cyklofosfamid škálované podľa dose level
    etop_pm = round(50 * factor, 2)
    doxo_pm = round(10 * factor, 2)
    cfa_pm = round(750 * factor, 2)
    etop_d = round(etop_pm * rbodysurf, 2);  etop_tot = round(etop_pm * 4 * rbodysurf, 2)
    doxo_d = round(doxo_pm * rbodysurf, 2);  doxo_tot = round(doxo_pm * 4 * rbodysurf, 2)
    cfa = round(cfa_pm * rbodysurf, 2)
    # Fixné dávky (nezávislé od dose level)
    vinc_d = round(0.4 * rbodysurf, 2); vinc_tot = round(1.6 * rbodysurf, 2)
    pred = round(60 * rbodysurf, 2)
    ritux = round(375 * rbodysurf, 2)

    if with_rituximab:
        st.write(f"rituximab 375 mg/m2 ......... {ritux} mg D1")
    st.write(f"etopozid {etop_pm} mg/m2/deň (CIV D1-4) ......... {etop_d} mg/deň (spolu {etop_tot} mg za 96h)")
    st.write(f"doxorubicin {doxo_pm} mg/m2/deň (CIV D1-4) ......... {doxo_d} mg/deň (spolu {doxo_tot} mg za 96h)")
    st.write(f"vinkristín 0.4 mg/m2/deň (CIV D1-4, BEZ stropu) ......... {vinc_d} mg/deň (spolu {vinc_tot} mg za 96h)")
    st.write(f"cyklofosfamid {cfa_pm} mg/m2 ......... {cfa} mg D5")
    st.write(f"prednizón 60 mg/m2 2× denne ......... {pred} mg 2× denne p.o. D1-5")
    st.write("NC 21. deň")
    st.write(" ")
    st.write("D1")
    st.write("Premedikácia: Palonosetron 0.5mg/Netupitant 300mg (Akynzeo) p.o. 1h pred chemo, Dexametazón 12mg i.v., Pantoprazol 40mg p.o." +
             (" Pred rituximabom: Hydrocortison 100mg i.v., Dithiaden 1amp i.v., Paracetamol 1g p.o. (1. infúzia: 50ml/h, postupne zvyšovať; ďalšie cykly 100ml/h)." if with_rituximab else ""))
    if with_rituximab:
        st.write(f"rituximab {ritux} mg v 500ml FR i.v. D1")
    st.write("D1-D4 — spoločná 96-hodinová kontinuálna infúzia (jedna pumpa/kivi):")
    st.write(f"  etopozid {etop_tot} mg + doxorubicin {doxo_tot} mg + vinkristín {vinc_tot} mg v 1000ml FR i.v. kontinuálne počas 96 hodín (D1-4)")
    st.write(f"D5: cyklofosfamid {cfa} mg v 500ml FR i.v./30-60 min")
    st.write(f"D1-D5: prednizón {pred} mg p.o. 2× denne")
    st.write("D6+: G-CSF (filgrastim) s.c. denne do obnovy počtu neutrofilov")
    st.write(" ")
    st.info("⚠️ **Dose-adjustment (Wilson protokol)** — podľa nadiru z PREDCHÁDZAJÚCEHO cyklu "
            "(monitorovať počty 2× týždenne):\n"
            "- ANC nadir ≥ 0.5 ×10⁹/L (nikdy nižšie) → **zvýš o 1 level**\n"
            "- ANC nadir < 0.5 pri 1-2 meraniach → **rovnaký level**\n"
            "- ANC nadir < 0.5 pri ≥3 meraniach ALEBO trombocyty < 25 ×10⁹/L → **zníž o 1 level**\n\n"
            "Cyklus 1 = vždy level 1. Upravujú sa len etopozid, doxorubicin a cyklofosfamid "
            "(o 20 % na level); vinkristín a prednizón ostávajú fixné.")

def main():
    """Main function to run the Streamlit app."""
    st.title("ChemoThon - HematologySK v. 2.3")
    st.write(" ")
    st.write("         Vitajte v programe ChemoThon!")
    st.write("""Program rozpisuje najbežnejšie chemoterapie podľa povrchu alebo hmotnosti.
    Najskôr si vypočítajte BSA a potom sa Vám sprístupní tlačidlo pre výpočet chemoterapie.
    Dávky je nutné upraviť podľa aktuálne dostupných balení liečiv.
    Autor nezodpovedá za prípadné škody spôsobené jeho použitím!
    Pripomienky a požiadavky na úpravu posielajte na filip.kohutek@fntn.sk""")

    weight = st.number_input("Zadajte hmotnosť (kg):", min_value=1, max_value=250, value=70, step=1)
    height = st.number_input("Zadajte výšku (cm):", min_value=1, max_value=250, value=170, step=1)

    if st.button("Vypočítať BSA"):
        rbodysurf = calculate_bsa(weight, height)
        st.session_state['rbodysurf'] = rbodysurf
        st.session_state['weight_kg'] = weight

    if 'rbodysurf' in st.session_state:
        st.write(f"Vypočítaný telesný povrch (BSA): {st.session_state['rbodysurf']} m²")

        chemo_options = {
            # --- Hodgkinov lymfóm ---
            "ABVD": ("ABVD.json", None),
            # --- Agresívne NHL (DLBCL) ---
            "R-CHOP": ("RCHOP.json", "flatvincristin.json"),
            "CHOP (bez R)": ("CHOP.json", "flatvincristin.json"),
            "R-miniCHOP (elderly)": ("RminiCHOP.json", "flatminivincristin.json"),
            "miniCHOP (bez R)": ("miniCHOP.json", "flatminivincristin.json"),
            # --- Indolentné NHL / CLL ---
            "R-CVP": ("RCVP.json", "flatvincristin.json"),
            "R-Bendamustin (BR)": ("BR.json", None),
            "Bendamustin (monoterapia 120mg/m2)": ("bendamustin.json", None),
            # --- Záchranné režimy ---
            "R-DHAP": ("RDHAP", None),
            "DHAP": ("DHAP", None),
            "DA-EPOCH-R (DLBCL/HG-BCL, CIV D1-4)": ("DAEPOCHR", None),
            "DA-EPOCH (bez R, CIV D1-4)": ("DAEPOCH", None),
            "R-Gemox": ("RGemox.json", None),
            "Gemox": ("Gemox.json", None),
            "GDP (Gemcitabin + Cisplatina + Dex)": ("GDP.json", "flatdexametazon.json"),
            # --- Iné ---
            "Rituximab (monoterapia)": ("rituximab.json", None),
            # --- Nové (2026-06) ---
            "Pola-R-CHP (DLBCL 1. línia, POLARIX)": ("pola_rchp.json", None),
            "BV-AVD (Hodgkin štádium III/IV, ECHELON-1)": ("bv_avd.json", None),
        }

        chemo_file = st.selectbox("Vyberte chemoterapeutický režim:", list(chemo_options.keys()))

        # Dose level výber pre DA-EPOCH (mimo tlačidla, aby pretrval pri prepočte)
        da_level = 1
        if chemo_file in ("DA-EPOCH-R (DLBCL/HG-BCL, CIV D1-4)", "DA-EPOCH (bez R, CIV D1-4)"):
            da_level = st.number_input(
                "Dose level (1 = baseline; ↑ ak ANC nadir ≥0.5, ↓ ak ANC<0.5 pri ≥3 meraniach alebo trombo <25). "
                "Redukciu pod level 1 rieš podľa inštitučného protokolu.",
                min_value=1, max_value=5, value=1, step=1)

        if st.button('Zobraziť protokol chemoterapie'):
            selected_option = chemo_options[chemo_file]
            if chemo_file == "DHAP":
                DHAP(st.session_state['rbodysurf'])
            elif chemo_file == "R-DHAP":
                RDHAP(st.session_state['rbodysurf'])
            elif chemo_file == "DA-EPOCH-R (DLBCL/HG-BCL, CIV D1-4)":
                DA_EPOCH(st.session_state['rbodysurf'], with_rituximab=True, dose_level=da_level)
            elif chemo_file == "DA-EPOCH (bez R, CIV D1-4)":
                DA_EPOCH(st.session_state['rbodysurf'], with_rituximab=False, dose_level=da_level)
            elif selected_option[1]:  # Flatdoser ak existuje druhý JSON
                Flatdoser(st.session_state['rbodysurf'], *selected_option)
            else:
                display_chemotherapy_details(st.session_state['rbodysurf'], selected_option[0])

if __name__ == "__main__":
    main()



# ===== Zdroje / Sources (pridané 2026-06, aditívne) =====
with st.expander("📚 Zdroje k režimom / Sources"):
    st.markdown("""**Kľúčové referencie – hematologické malignity**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-haematological-malignancies) · [NCCN](https://www.nccn.org/guidelines/category_1). Vždy overte podľa aktuálnej verzie guidelines a dostupných balení liečiv. Stav: jún 2026.

- **ABVD (Hodgkin)** — Canellos et al., NEJM 1992; eskalovaný BEACOPP – Diehl et al., NEJM 2003.
- **R-CHOP (DLBCL)** — GELA LNH-98.5 – Coiffier et al., NEJM 2002.
- **CHOP (bez R)** — Fisher et al., NEJM 1993.
- **R-miniCHOP (>80 r.)** — Peyrade et al., Lancet Oncol 2011.
- **R-CVP (indolentné NHL)** — Marcus et al., Blood 2005.
- **R-Bendamustín (BR)** — StiL NHL1 – Rummel et al., Lancet 2013; BRIGHT – Flinn et al., Blood 2014.
- **Bendamustín (monoterapia)** — CLL/relaps – Knauf et al., J Clin Oncol 2009.
- **R-DHAP / DHAP (salvage)** — Velasquez et al., Blood 1988; CORAL – Gisselbrecht et al., J Clin Oncol 2010.
- **DA-EPOCH-R (DLBCL / HG-BCL / primárny mediastinálny)** — Wilson et al., Blood 2002; Dunleavy et al., NEJM 2013 (PMBCL); CALGB 50303 – Bartlett et al., J Clin Oncol 2019.
- **R-Gemox / Gemox** — El Gnaoui et al., Ann Oncol 2007.
- **GDP (gemcitabín/cisplatina/dex)** — NCIC-CTG LY.12 – Crump et al., J Clin Oncol 2014.
- **Rituximab (monoterapia)** — McLaughlin et al., J Clin Oncol 1998.

- **Pola-R-CHP (POLARIX, DLBCL 1. línia)** — Tilly et al., NEJM 2022;386:351.
- **BV-AVD (ECHELON-1, Hodgkin štádium III/IV)** — Connors et al., NEJM 2018; Ansell et al., NEJM 2022.""")
