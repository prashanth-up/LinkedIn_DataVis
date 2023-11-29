# import streamlit as st
# import pandas as pd
# import janitor
# import networkx as nx
# from pyvis.network import Network
# from itertools import combinations

# # Function to process individual CSV
# def process_csv(uploaded_file):
#     df = pd.read_csv(uploaded_file, skiprows=3)
#     df = df.clean_names().drop(columns=['first_name', 'last_name', 'email_address']).dropna(subset=['company', 'position'])
#     df['connected_on'] = pd.to_datetime(df['connected_on'], format='%d %b %Y')
#     return df

# st.set_page_config(page_title="LinkedIn Network Graphs")
# st.title("Social Network Visualizer")

# uploaded_files = st.file_uploader("Choose LinkedIn Connections.csv files", accept_multiple_files=True)

# generate_button = st.button("Generate Network Graph")

# if uploaded_files and generate_button:
#     all_data = pd.concat([process_csv(file) for file in uploaded_files])

#     # Remove freelance/self-employed entries
#     pattern = "freelance|self-employed"
#     all_data = all_data[~all_data['company'].str.contains(pattern, case=False)]

#     # Create a network graph
#     G = nx.Graph()

#     # Add nodes and edges
#     for _, row in all_data.iterrows():
#         person = row['url']
#         company = row['company']
#         position = row['position']

#         # Add nodes
#         G.add_node(person, label=person, title=person, color='blue', size=10)
#         G.add_node(company, label=company, color='green', size=5)
#         G.add_node(position, label=position, color='red', size=5)

#         # Add edges
#         G.add_edge(person, company, color='grey')
#         G.add_edge(person, position, color='grey')

#     # Find common connections based on company and position
#     for company in all_data['company'].unique():
#         employees = all_data[all_data['company'] == company]['url']
#         for person1, person2 in combinations(employees, 2):
#             G.add_edge(person1, person2, color='orange', width=2)

#     for position in all_data['position'].unique():
#         holders = all_data[all_data['position'] == position]['url']
#         for person1, person2 in combinations(holders, 2):
#             G.add_edge(person1, person2, color='purple', width=2)

#     # Generate interactive graph
#     nt = Network('750px', '100%', bgcolor='#31333f', font_color='white')
#     nt.from_nx(G)
#     nt.show('network_graph.html')

#     # Display in Streamlit
#     HtmlFile = open('network_graph.html', 'r', encoding='utf-8')
#     st.components.v1.html(HtmlFile.read(), height=800)

#     # Download button for the graph
#     with open("network_graph.html", "rb") as file:
#         st.download_button(
#             label="Download network graph",
#             data=file,
#             file_name="network_graph.html",
#             mime="file/html"
#         )
# else:
#     if generate_button:
#         st.warning("Please upload files before generating the graph.")
