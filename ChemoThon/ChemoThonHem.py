import streamlit as st
import json

def load_json(filename):
    """ Načíta údaje JSON zo špecifikovaného súboru s ošetrením chýb. """
    try:
        with open(f'data/{filename}', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error(f"Súbor nenájdený: {filename}. Uistite sa, že je v adresári 'data'.")
        return None
    except json.JSONDecodeError:
        st.error("Chyba pri dekódovaní JSON. Skontrolujte formát súboru.")
        return None

def display_chemotherapy_details(rbodysurf, filename):
    """ Zobrazuje podrobné informácie o chemoterapeutickom režime s využitím telesného povrchu. """
    chemo_json = load_json(filename)
    if chemo_json:
        regimen_name = filename.replace('.json', '')
        st.write(f"### Protokol {regimen_name}")
        for chemo in chemo_json['Chemo']:
            dosage = round(chemo['Dosage'] * rbodysurf, 2)
            st.write(f"{chemo['Name']} {chemo['Dosage']} mg/m2 ......... {dosage} mg D {chemo['Day']}")

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


def Flatdoser(rbodysurf, chemoType, chemoFlat):
    """ Function to handle chemotherapy regimens that include flat-dose chemotherapy. """
    chemo_json = load_json(chemoType)
    chemo_json2 = load_json(chemoFlat)
    
    if chemo_json and chemo_json2:
        regimen_name = chemoType.replace('.json', '')
        st.write(f"### {regimen_name} Protocol")
        
        for chemo in chemo_json['Chemo']:
            dosage = round(chemo['Dosage'] * rbodysurf, 2)
            st.write(f"{chemo['Name']} {chemo['Dosage']} mg/m2 ......... {dosage} mg D {chemo['Day']}")
        
        for chemo in chemo_json2['Chemo']:
            st.write(f"{chemo['Name']} (flat dose) ......... {chemo['Dosage']} mg D {chemo['Day']}")

        st.write(f"                       NC {chemo_json.get('NC', 'Nie je určené')} . deň")
        
        # Adding a space before Day 1 section for better readability
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
            flat_dose = next((item['Dosage'] for item in chemo_json2['Chemo'] if item['Name'] == instruction['Name']), None)
            if flat_dose:
                st.write(f"{instruction['Name']} (flat dose): {flat_dose} mg {instruction['Inst']}")

def DHAP(rbodysurf):
    """ Špecifická funkcia pre chemoterapeutický režim DHAP. """
    DDP = round(rbodysurf * 100, 2)
    cycle = DDP // 50
    remnant = DDP % 50
    iremnant = int(remnant)
    icycle = int(cycle)

    st.write(f"cisplatina 100mg/m2........ {DDP} mg D1")
    st.write(f"cytarabin 2000mg/m2 BID....... {2000 * rbodysurf} mg každých 12 hodín D2")
    st.write("dexametazon 40mg .................... 40mg D1-D4")
    st.write("                                        NC 21. deň")
    st.write(" ")
    st.write("                                            D1")
    st.write("1. Ondasetron 8mg v 250ml FR iv, Dexametazon 8mg iv, Pantoprazol 40mg p.o.")

    for ordo in range(2, icycle + 2):
        st.write(f"{ordo}. cisplatina 50mg v 500ml RR iv")
    
    if iremnant > 0:
        st.write(f"{ordo}. cisplatina {iremnant} mg v 500ml RR iv")
        st.write(f"{ordo + 1}. manitol 10% 250ml iv")
        st.write(f"{ordo + 2}. dexametazon 40mg tableta p.o.")
    else:
        st.write(f"{ordo}. manitol 10% 250ml iv")
        st.write(f"{ordo + 1}. dexametazon 40mg tableta p.o.")

def calculate_bsa(weight, height):
    """ Vypočíta telesný povrch pomocou vzorca DuBois. """
    return round((weight**0.425) * (height**0.725) * 0.007184, 2)


def main():
    """Main function to run the Streamlit app."""
    st.title("ChemoThon - HematologySK v. 2.0")
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

    if 'rbodysurf' in st.session_state:
        st.write(f"Vypočítaný telesný povrch (BSA): {st.session_state['rbodysurf']} m²")  # Display BSA persistently

    chemo_options = {
        "ABVD": ("ABVD.json", None),
        "CHOP": ("CHOP.json", "flatvincristin.json"),
        "miniCHOP": ("miniCHOP.json", "flatminivincristin.json"),
        "DHAP": ("DHAP", None),  # Special handling for DHAP
        "Bendamustin": ("bendamustin.json", None),
        "Gemox": ("Gemox.json", None),
        "Rituximab": ("rituximab.json", None)
    }

    chemo_file = st.selectbox("Vyberte chemoterapeutický režim:", list(chemo_options.keys()))

    if 'rbodysurf' in st.session_state and st.button('Zobraziť protokol chemoterapie'):
        selected_option = chemo_options[chemo_file]
        if chemo_file == "DHAP":
            DHAP(st.session_state['rbodysurf'])
        elif selected_option[1]:  # Checks if there is a flat dose component
            Flatdoser(st.session_state['rbodysurf'], *selected_option)
        else:
            display_chemotherapy_details(st.session_state['rbodysurf'], selected_option[0])

if __name__ == "__main__":
    main()
