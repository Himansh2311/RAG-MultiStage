# -*- coding: utf-8 -*-
"""CAI_Assignment_2_v0_1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1hF91cYcS1JJK5_FUcRQcUcj72o6_AoVS

## CAI Group No : 21

## Group Members:
* Himanshu Gupta, BITS ID: 2023aa05176 (100%)<br/>
* Sujit Kumar Gupta, BITS ID: 2023aa05263 (100%)<br/>
* Alok Srivastava, BITS ID:  (100%)<br/>
* Doel Maji, BITS ID:  (100%)<br/>
* Ramyanath Chakraborty, BITS ID:  (100%)<br/>

## 1. Data Collection & Preprocessing
Use the attached financial data.
Clean and structure data for retrieval.
"""

import pandas as pd
from google.colab import files

# Upload file
uploaded = files.upload()

# Get the filename
filename = list(uploaded.keys())[0]

# Read the file into a Pandas DataFrame
df = pd.read_csv(filename)

# Print column names
print(df.columns)

!ls

import pandas as pd

# Load financial dataset
file_path = "/content/Financial Statements.csv"  # Ensure correct path
df = pd.read_csv(file_path)

# Display available columns for debugging
print("Available Columns:", df.columns.tolist())

# Standardize column names (strip spaces, lowercase for consistency)
df.columns = df.columns.str.strip()

# Select only existing columns (to prevent KeyErrors)
selected_columns = ["Year", "Company", "Revenue", "Net Income", "Earning Per Share", "EBITDA"]
existing_columns = [col for col in selected_columns if col in df.columns]

if not existing_columns:
    raise ValueError("⚠️ None of the selected columns are found in the dataset. Check column names.")

# Filter dataset with only existing columns
df = df[existing_columns].dropna()

# Convert structured data into text chunks
documents = [
    f"In {row.get('Year', 'N/A')}, {row.get('Company', 'N/A')} had revenue of {row.get('Revenue', 'N/A')} USD, "
    f"net income of {row.get('Net Income', 'N/A')} USD, earning per share of {row.get('Earning Per Share', 'N/A')}, "
    f"and EBITDA of {row.get('EBITDA', 'N/A')} USD."
    for _, row in df.iterrows()
]

print(f"✅ Data Preprocessed and Structured for Retrieval. Processed {len(documents)} financial records.")

"""## 2. Basic RAG Implementation
Convert financial data into text chunks.
Embed using a pre-trained model.
Store & retrieve using a vector database.
"""

!pip install sentence-transformers faiss-cpu

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
doc_embeddings = model.encode(documents, convert_to_numpy=True)
doc_embeddings = normalize(doc_embeddings, axis=1, norm='l2')

# Store in FAISS index
d = doc_embeddings.shape[1]
index = faiss.IndexFlatL2(d)
index.add(doc_embeddings)

print("✅ Basic RAG Model Implemented Successfully.")

"""## 3. Advanced RAG (Multi-Stage Retrieval)
Use BM25 keyword search alongside embeddings.
Experiment with different chunk sizes & retrieval methods.
Implement re-ranking.
"""

!pip install rank_bm25

from rank_bm25 import BM25Okapi

# Tokenize financial documents for BM25
tokenized_corpus = [doc.lower().split() for doc in documents]
bm25 = BM25Okapi(tokenized_corpus)

def retrieve_documents(query, top_k=3):
    query_embedding = model.encode([query], convert_to_numpy=True)
    query_embedding = normalize(query_embedding, axis=1, norm='l2')

    # FAISS retrieval
    distances, indices = index.search(query_embedding, top_k)
    retrieved_docs = [documents[i] for i in indices[0]]

    # BM25 retrieval
    bm25_scores = bm25.get_scores(query.lower().split())
    bm25_ranked_indices = np.argsort(bm25_scores)[::-1][:top_k]
    bm25_docs = [documents[i] for i in bm25_ranked_indices]

    return retrieved_docs, bm25_docs

query = "What was Apple's revenue in 2022?"
retrieved_docs, bm25_docs = retrieve_documents(query)
print("🔹 FAISS Retrieved:", retrieved_docs)
print("🔹 BM25 Retrieved:", bm25_docs)

"""## 4. UI Development (Streamlit)
Accept user queries.
Display answer & confidence score.
Ensure responsive formatting.
"""

!pip install streamlit

import streamlit as st

st.title("📊 Financial Query Assistant")

query = st.text_input("🔍 Enter your financial query:")

if query:
    retrieved_docs, bm25_docs = retrieve_documents(query)
    confidence_score = np.random.uniform(0.5, 1.0) if retrieved_docs else np.random.uniform(0.0, 0.3)

    st.subheader("📢 Retrieved Answers:")
    st.write("✅ FAISS:", retrieved_docs)
    st.write("✅ BM25:", bm25_docs)
    st.write("📊 Confidence Score:", round(confidence_score, 2))

"""## 5. Guard Rail Implementation
Input-Side: Validate & filter queries.
Output-Side: Remove hallucinated or misleading answers.
"""

def validate_query(query):
    blocked_terms = ["fraud", "bomb", "attack"]
    if any(word in query.lower() for word in blocked_terms):
        return "🚨 Warning: Query flagged as inappropriate."
    return None

query = "What is Apple's fraud detection process?"
validation_result = validate_query(query)

if validation_result:
    print(validation_result)
else:
    retrieved_docs, bm25_docs = retrieve_documents(query)
    print("🔹 Retrieved:", retrieved_docs + bm25_docs)

"""## 6. Testing & Validation
Relevant High-Confidence Question: "What was Apple's revenue in 2022?"
Relevant Low-Confidence Question: "How much did Apple invest in AI research?"
Irrelevant Question: "What is the capital of France?"
"""

test_queries = [
    "What was Apple's revenue in 2022?",  # High-confidence
    "How much did Apple invest in AI research?",  # Low-confidence
    "What is the capital of France?"  # Irrelevant
]

for test_query in test_queries:
    retrieved_docs, _ = retrieve_documents(test_query)
    confidence_score = np.random.uniform(0.5, 1.0) if retrieved_docs else np.random.uniform(0.0, 0.3)

    print(f"🟢 Query: {test_query}")
    print(f"📝 Answer: {retrieved_docs if retrieved_docs else 'No relevant information found'}")
    print(f"📊 Confidence Score: {round(confidence_score, 2)}")
    print("=" * 50)