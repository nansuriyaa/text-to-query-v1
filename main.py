import os
import streamlit as st
from dotenv import load_dotenv
from llama_index.core import (
    Document,
    VectorStoreIndex,
    Settings,
    StorageContext,
    load_index_from_storage
)
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
import pandas as pd
import urllib.parse
import json
from typing import List, Dict

# Load environment variables
load_dotenv()

# Set up Gemini API key
gemini_api_key = os.getenv('GEMINI_API_KEY')
if gemini_api_key is None:
    st.error("GEMINI_API_KEY is not set")
else:
    st.success("GEMINI_API_KEY is set")

# Database configuration
connection_string = os.getenv('DATABASE_URL')

# Determine database type
parsed_url = urllib.parse.urlparse(connection_string)
db_type = parsed_url.scheme


if db_type == 'postgresql':
    import psycopg2
    from psycopg2 import Error
elif db_type == 'mysql':
    import mysql.connector
    from mysql.connector import Error
else:
    st.error(f"Unsupported database type: {db_type}")
    st.stop()

CUSTOM_EXAMPLES = [
    
    # {
    #     "question": "How many iron and manganese blocks has been successfully auctioned since 2015",
    #     "sql_query": """
    #     SELECT * FROM mom_auction 
    #     WHERE lower(mineral) LIKE '%iron%' AND lower(mineral) like '%manganese%' 
    #     or mineral LIKE '%Fe%' AND mineral LIKE '%Mn%';
    #     """
    # }
]

def get_connection():
    if db_type == 'postgresql':
        return psycopg2.connect(connection_string)
    elif db_type == 'mysql':
        return mysql.connector.connect(
            host=parsed_url.hostname,
            user=parsed_url.username,
            password=parsed_url.password,
            database=parsed_url.path.lstrip('/'),
            port=parsed_url.port or 3306
        )

def get_tables():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if db_type == 'postgresql':
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
        elif db_type == 'mysql':
            cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        return tables
    except Error as e:
        st.error(f"Error: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_metadata(table_name):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if db_type == 'postgresql':
            query = f"""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable,
                    column_default,
                    (SELECT pg_catalog.col_description(c.oid, cols.ordinal_position::int)
                    FROM pg_catalog.pg_class c
                    WHERE c.oid = (SELECT ('"' || cols.table_name || '"')::regclass::oid)
                        AND c.relname = cols.table_name) AS column_comment
                FROM information_schema.columns cols
                WHERE table_name = '{table_name}'
            """
            cursor.execute(query)
            columns = cursor.fetchall()
            metadata = []
            for column in columns:
                metadata.append(f"Field: {column[0]}, Type: {column[1]}, "
                                f"Null: {'YES' if column[2] == 'YES' else 'NO'}, "
                                f"Default: {column[3]}, "
                                f"Comment: {column[4] or ''}")
        elif db_type == 'mysql':
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            metadata = []
            for column in columns:
                metadata.append(f"Field: {column[0]}, Type: {column[1]}, "
                                f"Null: {column[2]}, Key: {column[3]}, "
                                f"Default: {column[4]}, Extra: {column[5]}")
        return metadata
    except Error as e:
        st.error(f"Error: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

def generate_sql_query(user_prompt: str, query_engine: RetrieverQueryEngine) -> str:
    prompt = (
        f"You need to analyze this and write an SQL query in normal text (not even markdown) to answer the below natural language question. "
        f"Don't give any explanation, just write the query.\n"
        f"India has different Financial Year (FY) from April 1st to March 31st so FY24 or FY2023-24 or FY2023-2024 means from April 1st 2023 till March 31st 2024"
        f"Convert string into a lower string and search it both at database level and user input level"
        f"Mining lease (ML) is represented as ML and composite licence (CL) is represented as CL."
        f"Mining Lease: A contract that allows someone to use land to extract mineral"
        f"Composite Licence: A two-stage concession that allows for prospecting operations followed by mining operations. Composite licenses are for areas where the government has done preliminary exploration, but more exploration is needed by mining companies."
        f"Mineral blocks generally have 2 or more minerals as well for example iron and manganese blocks will have both iron and manganese"
        f"Answer questions one by one if multiple questions has been asked"
        f"Whenever user asks to list something display tables with all the details from the database"
        f"Question: {user_prompt}"
        f"SQL Query:"
    )
    
    response = query_engine.query(prompt)
    return response.response.strip()

def execute_sql_query(query: str) -> List[Dict]:
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True) if db_type == 'mysql' else conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        if db_type == 'postgresql':
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in results]
        return results, None
    except Error as e:
        return None, str(e)
    finally:
        if conn:
            cursor.close()
            conn.close()

# @st.cache_resource
def load_data():
    # Set up Gemini LLM
    llm = Gemini(
        model="models/gemini-1.5-flash",
        api_key=gemini_api_key
    )

    # Set up Gemini Embedding model
    embed_model = GeminiEmbedding(
        model_name="models/embedding-001",
        api_key=gemini_api_key
    )

    # Configure settings
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.chunk_size = 1024

    # Check if the index already exists
    if os.path.exists("./storage"):
        # Load the existing index
        storage_context = StorageContext.from_defaults(persist_dir="./storage")
        index = load_index_from_storage(storage_context)
    else:
        # Create a new index
        tables = get_tables()
        table_metadata = {}
        for table in tables:
            table_metadata[table] = get_metadata(table)
        
        documents = []
        for table_name, fields in table_metadata.items():
            table_info = f"Table: {table_name}\n"
            table_info += "\n".join(fields)
            documents.append(Document(text=table_info))
        
        for example in CUSTOM_EXAMPLES:
            example_doc = f"Question: {example['question']}\nSQL Query: {example['sql_query']}"
            documents.append(Document(text=example_doc))

        # Use SimpleNodeParser for chunking
        parser = SimpleNodeParser.from_defaults(chunk_size=5000)
        nodes = parser.get_nodes_from_documents(documents)

        # Create the index
        index = VectorStoreIndex(nodes)

        # Save the index
        index.storage_context.persist("./storage")

    # Create a retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=10
    )

    # Create a query engine
    query_engine = RetrieverQueryEngine.from_args(
        retriever,
        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)]
    )

    return query_engine

def main():
    st.title("Advanced RAG Database Metadata Chat")

    query_engine = load_data()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to know about the database?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            generated_sql = generate_sql_query(prompt, query_engine)
            st.markdown(f"Generated SQL Query:")
            st.code(generated_sql, language="sql")
            
            st.markdown("Query Results:")
            results, error = execute_sql_query(generated_sql)
            if error:
                st.error(f"Error executing the query: {error}")
            elif results:
                df_results = pd.DataFrame(results)
                st.table(df_results)
            else:
                st.info("The query returned no results.")
            
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"SQL Query: {generated_sql}\n\nResults:\n{df_results.to_string(index=False) if results else 'No results found.'}"
        })

    st.sidebar.header("Sample Queries")

    sample_queries = [
        "how many blocks were auctioned since 2015",
        "",

    ]

    for i, query in enumerate(sample_queries):
        st.sidebar.subheader(f"Sample Query {i+1}")
        st.sidebar.text(query)

if __name__ == "__main__":
    main()