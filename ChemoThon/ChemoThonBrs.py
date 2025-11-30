import streamlit as st
import json

def load_json(filename):
    """Loads JSON data from a specified file with error handling."""
    try:
        with open(f'data/{filename}', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error(f"Súbor nenájdený: {filename}. Uistite sa, že je v adresári 'data'.")
        return None
    except json.JSONDecodeError:
        st.error("Chyba pri dekódovaní JSON. Skontrolujte formát súboru.")
        return None

def display_chemotherapy_details(rbodysurf, chemoType, weight):
    """Displays detailed information about the chemotherapy regimen using body surface area or weight."""
    chemoJson = load_json(chemoType)
    if chemoJson:
        st.write(f"### Protokol {chemoType.replace('.json', '')}")
        day1_dose = ""
        for chemo in chemoJson["Chemo"]:
            # Fixed dose for X7/7, trastuzumabsc, and pertuzumab combo fixed-dose
            if chemoType in ["capecitabineX77.json", "trastuzumabsc.json", "firstpertuzumab.json", "elsepertuzumab.json"]:
                st.write(f"{chemo['Name']} {chemo['Dosage']} mg D {chemo['Day']}")
                day1_dose = f"{chemo['Name']} {chemo['Dosage']} mg"
            elif chemoType in ["TDM1.json", "TDx.json", "Sacgov.json", "firsttrastuzumabiv.json", "elsetrastuzumabiv.json"]:
                dosage = round(chemo["Dosage"] * weight, 2)
                st.write(f"{chemo['Name']} {chemo['Dosage']} {chemo['DosageMetric']} ......... {dosage} mg D {chemo['Day']}")
                day1_dose = f"{chemo['Name']} {dosage} mg"
            elif chemoType in ["firsttrastupertu.json", "elsetrastupertu.json"]:
                dosage = chemo["Dosage"]
                st.write(f"{chemo['Name']} {dosage} mg D {chemo['Day']}")
                day1_dose = f"{chemo['Name']} {dosage} mg"
            else:
                dosage = round(chemo["Dosage"] * rbodysurf, 2)
                st.write(f"{chemo['Name']} {round(chemo['Dosage'], 2)} {chemo['DosageMetric']} ......... {dosage} mg D {chemo['Day']}")
                day1_dose = f"{chemo['Name']} {dosage} mg"

        st.write(f"NC {chemoJson['NC']} . deň")
        st.write("D1")
        st.write(chemoJson["Day1"]["Premed"]["Note"])

        for instruction in chemoJson["Day1"]["Instructions"]:
            if instruction["Name"]:
                chemo_entry = next((item for item in chemoJson["Chemo"] if item["Name"] == instruction["Name"]), None)
                if chemo_entry:
                    if chemoType in ["TDM1.json", "TDx.json", "Sacgov.json", "firsttrastuzumabiv.json", "elsetrastuzumabiv.json"]:
                        dosage = round(chemo_entry["Dosage"] * weight, 2)
                        st.write(f"{instruction['Name']} {dosage} mg {instruction['Inst']}")
                    elif chemoType in ["firsttrastupertu.json", "elsetrastupertu.json"]:
                        st.write(f"{instruction['Name']} {instruction['Inst']}")
                    elif chemoType in ["capecitabineX77.json", "trastuzumabsc.json", "firstpertuzumab.json", "elsepertuzumab.json"]:
                        st.write(f"{instruction['Name']} {instruction['Inst']}")
                    else:
                        dosage = round(chemo_entry["Dosage"] * rbodysurf, 2)
                        st.write(f"{instruction['Name']} {dosage} mg {instruction['Inst']}")
            else:
                st.write(instruction["Inst"])

def calculate_bsa(weight, height):
    """Calculates body surface area using the DuBois formula."""
    bodysurf = (weight**0.425) * (height**0.725) * 0.007184
    return round(bodysurf, 2)

def main():
    st.title("ChemoThon - BreastSK v. 2.2")
    st.write("Vitajte v programe ChemoThon!")
    st.write("""Program rozpisuje najbežnejšie chemoterapie podľa povrchu alebo hmotnosti. 
    Najskôr si vypočítajte BSA a potom sa Vám sprístupní tlačidlo pre výpočet chemoterapie.
    Dávky je nutné upraviť podľa aktuálne dostupných balení liečiv.
    Autor nezodpovedá za prípadné škody spôsobené jeho použitím!
    Imunoterapiu nájdete na stránke https://immunothon.streamlit.app.
    Pripomienky a požiadavky na úrpavu posielajte na filip.kohutek@fntn.sk""")

    weight = st.number_input("Zadajte hmotnosť (kg):", min_value=1, max_value=250, step=1, value=None)
    height = st.number_input("Zadajte výšku (cm):", min_value=1, max_value=250, step=1, value=None)

    if st.button("Vypočítať BSA") and weight is not None and height is not None:
        rbodysurf = calculate_bsa(weight, height)
        st.session_state['rbodysurf'] = rbodysurf
        st.write(f"Telesný povrch je: {rbodysurf} m²")

    if 'rbodysurf' in st.session_state:
        st.write(f"Telesný povrch (BSA): {st.session_state['rbodysurf']} m²")

        chemo_options = {
            "AC": "AC.json",
            "DD-AC + G-CSF": "dd-AC.json",
            "EC": "EC.json",
            "Pertuzumab": "firstpertuzumab.json",  # Default value, overridden by radio button
            "TD-M1": "TDM1.json",
            "Trastuzumab SC": "trastuzumabsc.json",
            "Trastuzumab IV": "firsttrastuzumabiv.json",
            "Trastuzumab-deruxtecan": "TDx.json",
            "capecitabin": "capecitabine.json",
            "capecitabin X7/7": "capecitabineX77.json",
            "docetaxel + G-CSF": "docetaxelbreast.json",
            "eribulin": "eribulin.json",
            "gemcitabin": "gemcitabine.json",
            "paclitaxel": "paclitaxelweekly.json",
            "peg- doxorubicin": "pegdoxo.json",
            "Sacituzumab govitecan": "Sacgov.json",
            "vinorelbin p.o. weekly": "vinorelbinweekly.json",
            "Trastuzumab/Pertuzumab": "firsttrastupertu.json",
        }

        chemo_name = st.selectbox("Vyberte chemoterapeutický režim:", list(chemo_options.keys()))

        if chemo_name == "Pertuzumab":
            pertuzumab_option = st.radio("Zvoľte typ podania pertuzumabu:", ["Prvé podanie", "Ďalšie podania"])
            if pertuzumab_option == "Prvé podanie":
                selected_filename = "firstpertuzumab.json"
            else:
                selected_filename = "elsepertuzumab.json"

        if chemo_name == "Trastuzumab IV":
            trastuzumab_option = st.radio("Zvoľte typ podania trastuzumabu IV:", ["Prvé podanie", "Ďalšie podania"])
            if trastuzumab_option == "Prvé podanie":
                selected_filename = "firsttrastuzumabiv.json"
            else:
                selected_filename = "elsetrastuzumabiv.json"

        if chemo_name == "Trastuzumab/Pertuzumab":
            combo_option = st.radio("Zvoľte typ podania trastuzumabu/pertuzumabu:", ["Prvé podanie", "Ďalšie podania"])
            if combo_option == "Prvé podanie":
                selected_filename = "firsttrastupertu.json"
            else:
                selected_filename = "elsetrastupertu.json"

        else:
            if chemo_name != "Pertuzumab" and chemo_name != "Trastuzumab IV" and chemo_name != "Trastuzumab/Pertuzumab":
                selected_filename = chemo_options[chemo_name]

        if st.button('Zobraziť protokol chemoterapie') and weight is not None:
            display_chemotherapy_details(
                st.session_state['rbodysurf'], selected_filename, weight
            )
        else:
            if weight is None:
                st.error("Prosím, zadajte hmotnosť na výpočet chemoterapie.")

if __name__ == "__main__":
    main()