import streamlit as st
import json 

def Chemo(rbodysurf, chemoType):
    """This function displays chemotherapy regimens based on body surface area."""
    # Load chemotherapy data from a JSON file
    with open(f'data/{chemoType}', "r") as chemoFile:
        chemoJson = json.loads(chemoFile.read())

    # Display general chemotherapy details
    st.write(f"### Chemotherapy Protocol: {chemoType}")
    st.write(f"**Next Cycle (NC): Day {chemoJson['NC']}**")

    # Display chemotherapy regimens and dosages
    for chemo in chemoJson["Chemo"]:
        dosage = round(chemo["Dosage"] * rbodysurf, 2)
        st.write(f"{chemo['Name']}: {dosage}mg {chemo['DosageMetric']} on Day {chemo['Day']}")

    # Display Day 1 specific instructions
    st.write("### Day 1 Instructions:")
    st.write(chemoJson["Day1"]["Premed"]["Note"])
    for instruction in chemoJson["Day1"]["Instructions"]:
        adjusted_dosage = round(instruction["Dosage"] * rbodysurf, 2)
        st.write(f"{instruction['Name']}: {adjusted_dosage}mg {instruction['Inst']}")

def hematology(rbodysurf):
    st.subheader("Hematology Chemotherapy Selection")
    chemotherapy_options = {
        "ABVD": "ABVD.json",
        "CHOP": ("CHOP.json", "flatvincristin.json"),
        "miniCHOP": ("miniCHOP.json", "flatminivincristin.json"),
        "DHAP": "DHAP.json",
        "Bendamustin": "bendamustin.json",
        "GemOx": "Gemox.json",
        "Rituximab": "rituximab.json"
    }

    option = st.selectbox("Select the chemotherapy regimen:", list(chemotherapy_options.keys()))

    if st.button('Display Chemotherapy Protocol'):
        if isinstance(chemotherapy_options[option], tuple):
            chemo_json, flat_json = chemotherapy_options[option]
            Flatdoser(rbodysurf, chemo_json, flat_json)
        else:
            chemo_json = chemotherapy_options[option]
            Chemo(rbodysurf, chemo_json)

def diagnosis(rbodysurf, weight):
    st.subheader("Diagnosis and Chemotherapy Protocol Selection")
    diagnosis_options = {
        1: "Hematologic malignancies",
        2: "Breast cancer",
        3: "Lung cancer",
        4: "Colorectal cancer",
        5: "Other GIT malignancies",
        6: "Head and neck cancer",
        7: "Sarcomas, NET, and CNS tumors",
        8: "Urogenital malignancies",
        9: "Gynecological malignities"
    }
    choice = st.selectbox("Select the diagnosis you are treating:", options=list(diagnosis_options.values()), index=0)

    if st.button('Continue with Selected Diagnosis'):
        diagnosis_index = list(diagnosis_options.values()).index(choice) + 1
        if diagnosis_index == 1:
            hematology(rbodysurf)
        elif diagnosis_index == 2:
            breast(rbodysurf,weight)
        elif diagnosis_index == 3:
            lung(rbodysurf)
        elif diagnosis_index == 4:
            colorectal(rbodysurf, weight)
        elif diagnosis_index == 5:
            gastrointestinal(rbodysurf)
        elif diagnosis_index == 6:
            headandneck(rbodysurf)
        elif diagnosis_index == 7:
            sarcnet(rbodysurf)
        elif diagnosis_index == 8:
            urogenital(rbodysurf)
        elif diagnosis_index == 9:
            gynecology(rbodysurf)
        else:
            st.error("Invalid choice!")

def calculate_bsa(weight, height):
    """Calculate Body Surface Area using the DuBois formula."""
    bodysurf = (weight**0.425) * (height**0.725) * 0.007184
    return round(bodysurf, 2)

def main():
    st.title("Welcome to ChemoThon v1.0")
    st.write("""
    This application calculates chemotherapy dosages based on body surface area or body weight.
    Please adjust dosages according to currently available drug packages.
    The author is not responsible for any damages caused by the use of this tool.
    Feedback can be sent to filip.kohutek@fntn.sk
    """)
    
    # Sidebar for input
    with st.sidebar:
        st.header("Patient Data Input")
        weight = st.number_input("Enter Weight (kg):", min_value=1, max_value=250, step=1)
        height = st.number_input("Enter Height (cm):", min_value=1, max_value=250, step=1)
        
        if st.button("Calculate BSA"):
            rbodysurf = calculate_bsa(weight, height)
            st.write(f"Calculated Body Surface Area (BSA): {rbodysurf} m²")
            # This could be a placeholder to run additional functionality, like diagnosis or displaying protocols
            # For now, we'll just display the BSA in the main window
        
            diagnosis(rbodysurf, weight)

if __name__ == "__main__":
    main()
