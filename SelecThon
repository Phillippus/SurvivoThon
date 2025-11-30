import streamlit as st
import pandas as pd
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Initialize session state
if 'ledger' not in st.session_state:
    st.session_state['ledger'] = pd.DataFrame(columns=['Choice'])

def send_email(ledger, receiver_email):
    # Configure your email details securely
    sender_email = "your_email@gmail.com"
    sender_password = "your_password"

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'Ambulance Choice Report'

    # Email body
    body = ledger['Choice'].value_counts().to_frame().to_html()
    message.attach(MIMEText(body, 'html'))

    # SMTP server setup
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(message)
    server.quit()

    st.success('Report sent successfully!')

def record_choice(choice):
    # Add the choice to the ledger
    new_entry = pd.DataFrame({'Choice': [choice]})
    st.session_state['ledger'] = pd.concat([st.session_state['ledger'], new_entry], ignore_index=True)
    
    # Send an email after 100 uses
    if len(st.session_state['ledger']) >= 100:
        send_email(st.session_state['ledger'], 'receiver_email@example.com')
        st.session_state['ledger'] = pd.DataFrame(columns=['Choice'])  # Reset ledger

def main():
    st.title('Ambulance Selection App')

    ambulances = ['Chemoterapeutická ambulancia 8A', 'Chemoterapeutická ambulancia 8B', 'Chemoterapeutická ambulancia 8C']
    exclude_ambulance = st.selectbox('Exclude an ambulance (optional):', [''] + ambulances)
    filtered_ambulances = [ambulance for ambulance in ambulances if ambulance != exclude_ambulance]

    if st.button('Vyber ambulance náhodne!'):
        choice = random.choice(filtered_ambulances)
        st.success(f'Selected: {choice}')
        record_choice(choice)

    force_ambulance = st.selectbox('Or, force select an ambulance:', [''] + ambulances)
    if st.button('Force Selection') and force_ambulance:
        st.success(f'Forced Selection: {force_ambulance}')
        record_choice(force_ambulance)

    # Display the ledger
    st.write('Selection Ledger:')
    st.dataframe(st.session_state['ledger'])

if __name__ == '__main__':
    main()
