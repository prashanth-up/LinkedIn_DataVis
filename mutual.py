import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

def app():
    st.title("Mutual Connections Visualizer")

    # File upload
    uploaded_file_1 = st.file_uploader("Upload connections.csv file for Person 1", key="file1")
    uploaded_file_2 = st.file_uploader("Upload connections.csv file for Person 2", key="file2")

    if uploaded_file_1 and uploaded_file_2:
        df1 = pd.read_csv(uploaded_file_1, skiprows=3)
        df2 = pd.read_csv(uploaded_file_2, skiprows=3)

        # Dropdown for company and position filter
        all_companies = list(set(df1['Company']).union(set(df2['Company'])))
        all_positions = list(set(df1['Position']).union(set(df2['Position'])))
        company_filter = st.selectbox("Filter by Company", ["All"] + all_companies)
        position_filter = st.selectbox("Filter by Position", ["All"] + all_positions)

        # Apply filters
        if company_filter != "All":
            df1 = df1[df1['Company'] == company_filter]
            df2 = df2[df2['Company'] == company_filter]
        if position_filter != "All":
            df1 = df1[df1['Position'] == position_filter]
            df2 = df2[df2['Position'] == position_filter]

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
