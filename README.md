An end-to-end Retrieval-Augmented Generation (RAG) based customer support automation system that ingests domain knowledge, retrieves relevant context using vector search (ChromaDB / sklearn), generates intelligent responses, and automates Gmail draft creation and sending.

This system is designed to reduce manual customer support effort by automatically understanding user queries, fetching accurate information from a knowledge base, and responding via email.

🔍 Key Features

Knowledge Base Ingestion

Text documents are chunked and embedded

Stored in ChromaDB (persistent vector store)

Context-Aware Retrieval

Semantic search using embeddings

Top-K relevant chunks retrieved per query

RAG Pipeline

Retrieved context injected into response generation

Improves factual accuracy and relevance

Email Automation

Automatically creates Gmail drafts

Optional email sending support

Gmail OAuth2 integration

Multiple Indexing Options

ChromaDB

sklearn-based vector indexing

FAISS support (optional)

FastAPI Backend

REST APIs for processing support tickets

Swagger UI for testing

🏗️ Project Architecture
User Query
   ↓
FastAPI Endpoint
   ↓
Vector Retrieval (ChromaDB / sklearn)
   ↓
Context Injection (RAG)
   ↓
Response Generation
   ↓
Gmail Draft / Email Send
