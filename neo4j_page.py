import streamlit as st
from neo4j import GraphDatabase

def app():
    st.title("Neo4j Network Visualizer")

    # Neo4j database credentials and connection setup
    uri = "neo4j://localhost:7687"  # Replace with your Neo4j instance URI
    user = "neo4j"                 # Replace with your database username
    password = "password"          # Replace with your database password

    # Function to run a Cypher query
    def run_query(query):
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            results = session.run(query)
            return [record for record in results]
        driver.close()

    # Sample Cypher query (Modify according to your data)
    query = """
    MATCH (p:Person)-[r:CONNECTED_TO]->(other:Person)
    RETURN p.name AS person, collect(other.name) AS connections
    LIMIT 10
    """

    # Run the query and display results
    if st.button('Show Connections'):
        try:
            results = run_query(query)
            if results:
                for record in results:
                    st.write(f"Person: {record['person']}, Connections: {record['connections']}")
            else:
                st.write("No results found.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

