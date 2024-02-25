import pandas as pd
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test
from docx import Document
import matplotlib.pyplot as plt

# Function to validate user input for file path and column names
def validate_input(prompt, validation_set=None):
    while True:
        user_input = input(prompt).strip()
        # If a validation set is provided, check if the input is valid
        if validation_set is not None:
            if user_input in validation_set:
                return user_input
            else:
                print("Invalid input. Please try again.")
        else:
            # If no validation set is provided, return the input directly
            return user_input

# Load the data and validate the file path
while True:
    try:
        file_path = validate_input("Enter the path of the CSV file: ")
        data = pd.read_csv(file_path)
        break  # Exit loop if file is successfully loaded
    except FileNotFoundError:
        print("File not found. Please check the path and try again.")

# Obtain and validate column names
column_names = data.columns.tolist()
group_variable = validate_input("Enter the name of the independent variable (e.g., 'Obesity', 'PNI45'): ", column_names)
event_column = validate_input("Enter the name of the event column: ", column_names)
survival_time_column = validate_input("Enter the name of the survival time column: ", column_names)

# Input prompts for export file paths
docx_export_path = validate_input("Enter the path and filename for the DOCX export (e.g., 'results/KM_Analysis_Results.docx'): ")
image_export_path = validate_input("Enter the path and filename for the image export (e.g., 'results/KM_Curves.png'): ")

# Kaplan-Meier Fitter and analysis logic...
# (Include the rest of the Kaplan-Meier analysis and document creation logic here)

print(f"Results saved to {docx_export_path}")
print(f"Kaplan-Meier curves saved to {image_export_path}")
