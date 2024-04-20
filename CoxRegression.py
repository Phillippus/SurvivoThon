import streamlit as st
import pandas as pd
from lifelines import CoxPHFitter
import matplotlib.pyplot as plt

# Title of the app
st.title("Cox Proportional Hazards Regression Analysis")

# Upload CSV data
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    # Reading the data
    data = pd.read_csv(uploaded_file)
    st.write("Data Preview:")
    st.write(data.head())

    # User inputs for data
    duration_col = st.selectbox("Select Duration Column", options=data.columns)
    event_col = st.selectbox("Select Event Column", options=data.columns)
    covariate_cols = st.multiselect("Select Covariate Columns (Optional)", options=[col for col in data.columns if col not in [duration_col, event_col]])

    if st.button("Run Analysis"):
        # Ensure only selected covariate columns are included
        selected_columns = [duration_col, event_col] + covariate_cols
        data_for_analysis = data[selected_columns]

        # Fit the Cox model
        cph = CoxPHFitter()
        cph.fit(data_for_analysis, duration_col=duration_col, event_col=event_col)
        
        # Displaying the summary
        st.write("Cox Regression Results:")
        st.write(cph.summary)

        # Plotting survival curves
        fig, ax = plt.subplots()
        cph.plot(ax=ax)
        st.pyplot(fig)
