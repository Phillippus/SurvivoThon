import json
import os

def prompt_for_next_action():
    """Prompt the user for the next action regarding chemotherapy planning."""
    while True:
        action = input("Do you wish to plan another chemotherapy session? (y/n): ").lower().strip()
        if action == "y":
            start_chemotherapy_planning()
        elif action == "n":
            print("Exiting program.")
            quit()
        else:
            print("Invalid input. Please enter 'y' for yes or 'n' for no.")

def load_chemotherapy_data(chemo_type):
    """Load chemotherapy data from a JSON file."""
    data_path = os.path.join("data", f"{chemo_type}.json")
    try:
        with open(data_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file '{data_path}' was not found. Please check the file name and try again.")
    except json.JSONDecodeError:
        print(f"Error: There was an issue decoding the JSON data from '{data_path}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None

def calculate_and_display_dosage(chemo_data, body_surface_area):
    """Calculate and display the chemotherapy dosage based on the provided data."""
    if not chemo_data:
        print("No chemotherapy data provided.")
        return
    for item in chemo_data.get("Chemo", []):
        dosage = round(item["Dosage"] * body_surface_area, 2)
        print(f"{item['Name']} {dosage}{item['DosageMetric']} on Day {item['Day']}")

def start_chemotherapy_planning():
    """Main function to handle chemotherapy planning."""
    chemo_type = input("Enter the type of chemotherapy: ")
    body_surface_area = float(input("Enter the patient's body surface area (m^2): "))
    chemo_data = load_chemotherapy_data(chemo_type)
    calculate_and_display_dosage(chemo_data, body_surface_area)
    prompt_for_next_action()

if __name__ == "__main__":
    start_chemotherapy_planning()
