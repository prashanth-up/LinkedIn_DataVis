import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

def app():
    st.title("Mutual Connections Visualizer")

    uploaded_file_1 = st.file_uploader("Upload connections.csv file for Person 1", key="file1")
    uploaded_file_2 = st.file_uploader("Upload connections.csv file for Person 2", key="file2")

    if uploaded_file_1 and uploaded_file_2:
        df1 = pd.read_csv(uploaded_file_1, skiprows=3)
        df2 = pd.read_csv(uploaded_file_2, skiprows=3)

        # Combined DataFrame
        combined_df = pd.concat([df1, df2])

        # Unique companies and positions
        all_companies = combined_df['Company'].dropna().unique().tolist()
        all_positions = combined_df['Position'].dropna().unique().tolist()

        # Company and Position Filters with dynamic updating
        selected_company = st.selectbox("Filter by Company", ['All'] + all_companies, format_func=lambda x: '' if x == 'All' else x)
        filtered_positions = ['All'] + list(combined_df[combined_df['Company'] == selected_company]['Position'].dropna().unique()) if selected_company != 'All' else all_positions
        selected_position = st.selectbox("Filter by Position", filtered_positions, format_func=lambda x: '' if x == 'All' else x)

        # Filter DataFrame based on selections
        if selected_company != 'All':
            df1 = df1[df1['Company'] == selected_company]
            df2 = df2[df2['Company'] == selected_company]
        if selected_position != 'All':
            df1 = df1[df1['Position'] == selected_position]
            df2 = df2[df2['Position'] == selected_position]


        # Identify mutual connections
        mutual_companies = set(df1['Company']).intersection(set(df2['Company']))
        mutual_positions = set(df1['Position']).intersection(set(df2['Position']))

        # Create a graph
        G = nx.Graph()
        for _, row in df1.iterrows():
            G.add_node(row['First Name'] + ' ' + row['Last Name'], type='person')
            if row['Company'] in mutual_companies:
                G.add_node(row['Company'], type='company')
                G.add_edge(row['First Name'] + ' ' + row['Last Name'], row['Company'])
            if row['Position'] in mutual_positions:
                G.add_node(row['Position'], type='position')
                G.add_edge(row['First Name'] + ' ' + row['Last Name'], row['Position'])

        for _, row in df2.iterrows():
            G.add_node(row['First Name'] + ' ' + row['Last Name'], type='person')
            if row['Company'] in mutual_companies:
                G.add_node(row['Company'], type='company')
                G.add_edge(row['First Name'] + ' ' + row['Last Name'], row['Company'])
            if row['Position'] in mutual_positions:
                G.add_node(row['Position'], type='position')
                G.add_edge(row['First Name'] + ' ' + row['Last Name'], row['Position'])

        # Visualization
        pos = nx.spring_layout(G, k=0.1, iterations=20)
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_x = []
        node_y = []
        hover_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            hover_text.append(f"{node}<br>Type: {G.nodes[node]['type']}")

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=hover_text,
            marker=dict(
                showscale=False,
                color=[('blue' if G.nodes[node]['type'] == 'company' else 
                        'green' if G.nodes[node]['type'] == 'position' else 'red') for node in G.nodes()],
                size=10,
                line_width=2))

        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title='<br>Mutual Connections Network Graph',
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20,l=5,r=5,t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )

        st.plotly_chart(fig)
