import pandas as pd
import plotly.express as px
import janitor
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import networkx as nx
import json
import plotly.graph_objects as go
from wordcloud import WordCloud
import numpy as np
np.bool = np.bool_

def main():
    st.title("Social Network Visualizer")

    uploaded_file = st.file_uploader("Choose your LinkedIn Connections.csv file")
    uploaded_file_1 = st.file_uploader("Upload connections.csv file for Person 1", key="file1")
    uploaded_file_2 = st.file_uploader("Upload connections.csv file for Person 2", key="file2")

    if uploaded_file is not None:
        process_main_page(uploaded_file)

    if uploaded_file_1 is not None and uploaded_file_2 is not None:
        process_mutual_page(uploaded_file_1, uploaded_file_2)

def process_main_page(uploaded_file_1):
    df_ori = pd.read_csv(uploaded_file_1, skiprows=0) 
    
    df = (
        df_ori
        .clean_names()
        # .drop(columns=['first_name', 'last_name', 'email_address']) 
        .dropna(subset=['company', 'position'])
    )
    
    # Convert column names to lowercase
    df.columns = df.columns.str.lower()


    # Check if DataFrame is empty or if 'Connected On' column is missing
    if df.empty or 'connected_on' not in df.columns:
        st.error("The uploaded file is empty or does not contain a 'connected_on' column.")
        st.write("DataFrame columns found:", df.columns)  # Debugging line to check the columns
        return

    df['connected_on'] = pd.to_datetime(df['connected_on'], format='%d-%b-%y')
    
    def plot_timeline(df):
        # Adjust the datetime format to match the 'Connected On' column
        df['connected_on'] = pd.to_datetime(df['connected_on'], format='%d-%b-%y')
        fig_timeline = px.histogram(df, x='connected_on', nbins=50)
        st.plotly_chart(fig_timeline)


    def plot_company_distribution(df):
        fig_companies = px.bar(df['company'].value_counts().reset_index(), 
                            x='index', y='company', labels={'index': 'company', 'company': 'Count'})
        st.plotly_chart(fig_companies)

    def plot_position_distribution(df):
        fig_positions = px.bar(df['position'].value_counts().reset_index(), 
                            x='index', y='position', labels={'index': 'position', 'position': 'count'})
        st.plotly_chart(fig_positions)

    def plot_company_pie_chart(df):
        fig = px.pie(df, names='company')
        st.plotly_chart(fig)

    def plot_position_pie_chart(df):
        fig = px.pie(df, names='position')
        st.plotly_chart(fig)

    

    def plot_word_cloud(df):
        text = ' '.join(df['company'].dropna().tolist() + df['position'].dropna().tolist())
        wordcloud = WordCloud(width=800, height=400).generate(text)
        st.image(wordcloud.to_array())

    def plot_heatmap(df):
        heatmap_data = pd.crosstab(df['company'], df['position'])
        fig = px.imshow(heatmap_data, aspect='auto')
        st.plotly_chart(fig)

    # Checkboxes for visualizations
    show_timeline = st.checkbox("Show Timeline of Connections", value=True)
    if show_timeline:
        plot_timeline(df)
    show_company_bar_chart = st.checkbox("Show Bar Chart of Companies", value=True)
    if show_company_bar_chart:
        plot_company_distribution(df)
    show_position_bar_chart = st.checkbox("Show Bar Chart of Positions", value=True)
    if show_position_bar_chart:
        plot_position_distribution(df)
    show_company_pie_chart = st.checkbox("Show Pie Chart for Company Distribution", value=True)
    if show_company_pie_chart:
        plot_company_pie_chart(df)
    show_position_pie_chart = st.checkbox("Show Pie Chart for Position Distribution", value=True)
    if show_position_pie_chart:
        plot_position_pie_chart(df)
    show_word_cloud = st.checkbox("Show Word Cloud for Companies and Positions", value=True)
    if show_word_cloud:
        plot_word_cloud(df)
    show_heatmap = st.checkbox("Show Heatmap for Company vs. Position", value=False)
    if show_heatmap:
        plot_heatmap(df)
    



    
    pattern = "freelance|self-employed"
    df = df[~df['company'].str.contains(pattern, case=False)]

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

    def adjust_physics(network, non_overlapping):
        if non_overlapping:
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

        options_json = json.dumps({"physics": physics_options})
        network.set_options(options_json)

    df_company_reduced = df_company[df_company['count'] >= count_option]
    df_position_reduced = df_pos[df_pos['count'] >= position_option]

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
    adjust_physics(nt, non_overlapping_physics)  

    nt.show('company_graph.html')
    st.header('Connections by Company Graph')
    
    HtmlFile = open('company_graph.html', 'r', encoding='utf-8')
    components.html(HtmlFile.read(), height=800)

    p = nx.Graph()
    p.add_node(root_name)

    for _, row in df_position_reduced.iterrows():
        position = row['position']
        count = row['count']
        p.add_node(position, size=count*5, title=str(count), color=network_color(count, len(df_position_reduced), color_network_option))
        p.add_edge(root_name, position, color='grey')

    nt = Network('750px', '100%', bgcolor='#31333f', font_color='white')
    nt.from_nx(p)
    adjust_physics(nt, non_overlapping_physics)  

    nt.show('position_graph.html')
    st.header('Connections by Position Graph')
    HtmlFile = open('position_graph.html', 'r', encoding='utf-8')
    components.html(HtmlFile.read(), height=800)


def process_mutual_page(uploaded_file_1, uploaded_file_2):
    df1 = pd.read_csv(uploaded_file_1, skiprows=0)
    df2 = pd.read_csv(uploaded_file_2, skiprows=0)

    # # Convert column names to lowercase
    # df1.columns = df1.columns.str.lower()
    # df2.columns = df2.columns.str.lower()


    combined_df = pd.concat([df1, df2])
   

    # st.write("DataFrame columns found:", combined_df.columns)  # Debugging line to check the columns
    all_companies = combined_df['Company'].dropna().unique().tolist()
    all_positions = combined_df['Position'].dropna().unique().tolist()

    selected_company = st.selectbox("Filter by Company", ['All'] + all_companies, format_func=lambda x: '' if x == 'All' else x)
    filtered_positions = ['All'] + list(combined_df[combined_df['Company'] == selected_company]['Position'].dropna().unique()) if selected_company != 'All' else all_positions
    selected_position = st.selectbox("Filter by Position", filtered_positions, format_func=lambda x: '' if x == 'All' else x)

    if selected_company != 'All':
        df1 = df1[df1['Company'] == selected_company]
        df2 = df2[df2['Company'] == selected_company]

    if selected_position != 'All':
        df1 = df1[df1['Position'] == selected_position]
        df2 = df2[df2['Position'] == selected_position]

    mutual_companies = set(df1['Company']).intersection(set(df2['Company']))
    mutual_positions = set(df1['Position']).intersection(set(df2['Position']))

    G = nx.Graph()
    for _, row in df1.iterrows():
        G.add_node(row['First Name'] + ' ' + row['Last Name'], type='person', title=row.to_dict())
        if row['Company'] in mutual_companies:
            G.add_node(row['Company'], type='Company', title=row['Company'])
            G.add_edge(row['First Name'] + ' ' + row['Last Name'], row['Company'])
        if row['Position'] in mutual_positions:
            G.add_node(row['Position'], type='Position', title=row['Position'])
            G.add_edge(row['First Name'] + ' ' + row['Last Name'], row['Position'])

    for _, row in df2.iterrows():
        G.add_node(row['First Name'] + ' ' + row['Last Name'], type='person', title=row.to_dict())
        if row['Company'] in mutual_companies:
            G.add_node(row['Company'], type='Company', title=row['Company'])
            G.add_edge(row['First Name'] + ' ' + row['Last Name'], row['Company'])
        if row['Position'] in mutual_positions:
            G.add_node(row['Position'], type='position', title=row['Position'])
            G.add_edge(row['First Name'] + ' ' + row['Last Name'], row['Position'])

    # Plotly Graph
    pos = nx.spring_layout(G)

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')

    node_x = []
    node_y = []
    node_info = []
    node_size = []
    node_color = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_info.append(G.nodes[node]['title'])
        if G.nodes[node]['type'] == 'company':
            node_size.append(50)
            node_color.append('blue')
        elif G.nodes[node]['type'] == 'position':
            node_size.append(35)
            node_color.append('green')
        else:
            node_size.append(10)
            node_color.append('red')

    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers', hoverinfo='text', text=node_info, marker=dict(size=node_size, color=node_color, line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(showlegend=False, hovermode='closest', margin=dict(b=0, l=0, r=0, t=0)))
    st.plotly_chart(fig, use_container_width=True)

    # Pyvis Network Graph
    nt = Network('750px', '100%', bgcolor='#31333f', font_color='white')
    nt.from_nx(G)
    nt.show('mutual_graph.html')
    st.header('Mutual Connections Graph')

    HtmlFile = open('mutual_graph.html', 'r', encoding='utf-8')
    st.components.v1.html(HtmlFile.read(), height=800)

    
if __name__ == "__main__":
    main()
