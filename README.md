# 🚀 RAG-Powered Customer Support Automation System

> An end-to-end **Retrieval-Augmented Generation (RAG)** based customer support automation platform that intelligently answers customer queries using a knowledge base and automates Gmail responses.

---

## 📌 Overview

This project automates customer support by combining **semantic search** with **context-aware response generation**.  
User queries are matched against a domain knowledge base using vector embeddings, and accurate responses are generated and sent via **Gmail automation**.

---

## ✨ Key Features

- 🔍 **Semantic Knowledge Retrieval (RAG)**
- 🧠 **Context-Aware Response Generation**
- 📚 **ChromaDB Persistent Vector Store**
- 📩 **Automated Gmail Draft Creation & Sending**
- ⚡ **FastAPI Backend with Swagger UI**
- 🧩 **Multiple Indexing Options (Chroma / sklearn / FAISS)**

---

## 🏗️ System Architecture

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
