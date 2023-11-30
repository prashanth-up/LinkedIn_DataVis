import streamlit as st
from multiapp import MultiApp
import main_page
import mutual

# Set up the page configuration here. This should be the first Streamlit command.
st.set_page_config(page_title="Social Network Visualizer")

# Create an instance of the multi-page app
app = MultiApp()

# Title for the entire app
st.title("Social Network Visualizer")

# Add your application pages here
app.add_app("LinkedIn Network", main_page.app)
app.add_app("Mutual Network", mutual.app)

# Run the app
app.run()
