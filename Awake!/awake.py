import time
import requests

# Replace with your Streamlit app URL
app_url = "https://rescaleme.streamlit.app"

def ping_streamlit_app():
    try:
        response = requests.get(app_url)
        if response.status_code == 200:
            print(f"Successfully pinged the Streamlit app: {response.status_code}")
        else:
            print(f"Failed to ping the Streamlit app: {response.status_code}")
    except Exception as e:
        print(f"Error pinging the Streamlit app: {e}")

if __name__ == "__main__":
    while True:
        ping_streamlit_app()
        # Wait for 15 minutes before pinging again
        time.sleep(21600) 