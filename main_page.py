import pandas as pd
import janitor
from janitor import clean_names
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components  # Correct import for components
from pyvis.network import Network
import networkx as nx
import json

def app():
    # Set Streamlit page configuration
    # st.set_page_config(page_title="LinkedIn Network Graphs")
    st.title("Social Network Visualizer")

    # File uploader for LinkedIn data
    uploaded_file = st.file_uploader("Choose your LinkedIn Connections.csv file")
    if uploaded_file is None:
        st.warning('Please upload a LinkedIn connections.csv file to begin.')
        st.stop()
    # Read and preprocess the data
    df_ori = pd.read_csv(uploaded_file, skiprows=3)  # Skip the top 3 rows
    df = (
        df_ori
        .clean_names()
        .drop(columns=['first_name', 'last_name', 'email_address'])  # Privacy reasons
        .dropna(subset=['company', 'position'])
    )

    # Convert 'connected_on' to datetime
    df['connected_on'] = pd.to_datetime(df['connected_on'], format='%d %b %Y')

    # Filter out specific patterns
    pattern = "freelance|self-employed"
    df = df[~df['company'].str.contains(pattern, case=False)]

    # Sidebar options for the graph
    st.sidebar.title('Graph Options')
    color_option = st.sidebar.selectbox(
        'Color palette for bar graphs:',
        ('Tealgrn', 'Magenta', 'Rainbow', 'Plotly3', 'Inferno', 'Sunset', 'Cividis', 'Purple-Blue', 'Teal', 'Pink-Yellow')
    )

    

    def str_to_class(name):
        return getattr(px.colors.sequential, name, px.colors.sequential.Tealgrn)

    graph_option = st.sidebar.radio(
        label='Select a network graph layout:',
        options=('Packed graph', 'Spoked graph')
    )

    color_network_option = st.sidebar.selectbox(
        'Color palette for network graphs:',
        ('Bolds', 'Pastels', 'Bluegreen', 'Blues', 'Neons')
    )

    def network_color(count, total, color_choice):
        # Color palettes for network nodes
        Bolds = ['#10EDF5', '#28BCE0', '#556CBC', '#7343A9', '#9B0F8C', '#B8007F']
        Pastels = ['#9C82B5', '#C493C9', '#E88EBB', '#FEA2AF', '#FDD6CF', '#FFEDDF']
        Bluegreen = ['#0D98BB', '#2AA7BC', '#47B6BC', '#65C4BD', '#82D3BD', '#9FE2BE']
        Blues = ['#088CFF', '#36A3FF', '#64BAFE', '#91D1FE', '#BFE8FD', '#EDFFFD']
        Neons = ['#FCFF64', '#444AFF', '#FFB6F4', '#F9008F', '#39FF12', '#9D0BFA']
        ratio = int(count) / total
        if ratio >= .833:
            return eval(color_choice)[0]
        elif ratio >= .667:
            return eval(color_choice)[1]
        elif ratio >= .50:
            return eval(color_choice)[2]
        elif ratio >= .33:
            return eval(color_choice)[3]
        elif ratio >= .166:
            return eval(color_choice)[4]
        else:
            return eval(color_choice)[5]


    count_option = st.sidebar.slider('Minimum connections at a company:', 1, 20, 3)
    position_option = st.sidebar.slider('Minimum position titles:', 1, 20, 3)
    root_name = st.sidebar.text_input("Your name for the network diagrams:")

    # Creating bar graphs
    df_company = df['company'].value_counts().reset_index()
    df_company.columns = ['company', 'count']
    df_top_co = df_company.sort_values(by='count', ascending=False).head(15)

    co_graph = px.bar(
        df_top_co, x='count', y='company', color='count',
        orientation='h', color_continuous_scale=str_to_class(color_option)
    ).update_layout(yaxis_categoryorder="total ascending")

    st.header('Connections by Company')
    st.plotly_chart(co_graph)

    df_pos = df['position'].value_counts().reset_index()
    df_pos.columns = ['position', 'count']
    df_top_pos = df_pos.sort_values(by='count', ascending=False).head(15)

    pos_graph = px.bar(
        df_top_pos, x='count', y='position', color='count',
        orientation='h', color_continuous_scale=str_to_class(color_option)
    ).update_layout(yaxis_categoryorder="total ascending")

    st.header('Connections by Position')
    st.plotly_chart(pos_graph)
    non_overlapping_physics = st.checkbox("Enable non-overlapping graph physics", value=True)

    

    # Function to adjust physics for non-overlapping nodes
    def adjust_physics(network, non_overlapping):
        if non_overlapping:
            # Physics settings to prevent overlap
            physics_options = {
                "barnesHut": {
                    "gravitationalConstant": -30000,
                    "centralGravity": 0.3,
                    "springLength": 250,
                    "springConstant": 0.04,
                    "damping": 0.09,
                    "avoidOverlap": 0.1
                },
                "minVelocity": 0.75
            }
        else:
            # Default physics settings (may allow overlap)
            physics_options = {
            "barnesHut": {
                "gravitationalConstant": -20000,
                "centralGravity": 0.2,
                "springLength": 200,
                "springConstant": 0.05,
                "damping": 0.09
            },
            "stabilization": {"iterations": 150},
            "minVelocity": 1.0
        }

        # Convert physics options to JSON and set it
        options_json = json.dumps({"physics": physics_options})
        network.set_options(options_json)

    # Preparing data for network graph
    df_company_reduced = df_company[df_company['count'] >= count_option]
    df_position_reduced = df_pos[df_pos['count'] >= position_option]

    # Network graph for company connections
    g = nx.Graph()
    g.add_node(root_name)

    for _, row in df_company_reduced.iterrows():
        company = row['company']
        count = row['count']
        title = f"<b>{company}</b> – {count}"
        positions = set(df[df['company'] == company]['position'])
        positions_html = ''.join(f'<li>{pos}</li>' for pos in positions)
        hover_info = title + f"<ul>{positions_html}</ul>"
        g.add_node(company, size=count*5, title=hover_info, color=network_color(count, len(df_company_reduced), color_network_option))
        g.add_edge(root_name, company, color='grey')

    nt = Network('750px', '100%', bgcolor='#31333f', font_color='white')
    nt.from_nx(g)
    adjust_physics(nt, non_overlapping_physics)  # pass the checkbox state here

    nt.show('company_graph.html')
    st.header('Connections by Company Graph')
    
    HtmlFile = open('company_graph.html', 'r', encoding='utf-8')
    components.html(HtmlFile.read(), height=800)

    # Network graph for position connections
    p = nx.Graph()
    p.add_node(root_name)

    for _, row in df_position_reduced.iterrows():
        position = row['position']
        count = row['count']
        p.add_node(position, size=count*5, title=str(count), color=network_color(count, len(df_position_reduced), color_network_option))
        p.add_edge(root_name, position, color='grey')

    nt = Network('750px', '100%', bgcolor='#31333f', font_color='white')
    nt.from_nx(p)
    adjust_physics(nt, non_overlapping_physics)  # pass the checkbox state here

    nt.show('position_graph.html')
    st.header('Connections by Position Graph')
    HtmlFile = open('position_graph.html', 'r', encoding='utf-8')
    components.html(HtmlFile.read(), height=800)

