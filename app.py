#!/usr/bin/env python3
"""
Streamlit Web App for RAG System
Easy deployment to Streamlit Cloud, Railway, or any hosting
"""
import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
from src.backend.vectorize import VectorDB
from src.backend.llm import LLMAnswerGenerator

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="RAG Document Q&A",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = None
if 'llm' not in st.session_state:
    st.session_state.llm = None
if 'history' not in st.session_state:
    st.session_state.history = []


def initialize_rag():
    """Initialize RAG components"""
    try:
        # Initialize vector DB
        if st.session_state.db is None:
            with st.spinner("Loading document database..."):
                st.session_state.db = VectorDB()
                stats = st.session_state.db.get_collection_stats()
                st.success(f"✅ Loaded {stats['document_count']} document chunks")

        # Initialize LLM
        if st.session_state.llm is None:
            provider = st.session_state.get('llm_provider', 'anthropic')

            # Check for API keys
            if provider == 'anthropic':
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if not api_key or api_key == 'your_anthropic_api_key_here':
                    st.error("❌ ANTHROPIC_API_KEY not set in environment")
                    return False
            elif provider == 'openai':
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    st.error("❌ OPENAI_API_KEY not set in environment")
                    return False

            with st.spinner(f"Loading {provider} LLM..."):
                st.session_state.llm = LLMAnswerGenerator(provider=provider)
                st.success(f"✅ {provider.title()} LLM ready")

        return True

    except Exception as e:
        st.error(f"❌ Error initializing RAG: {str(e)}")
        return False


def query_rag(question: str, min_similarity: float = 60.0, n_results: int = 5):
    """Query the RAG system"""
    try:
        # Query vector DB
        with st.spinner("Searching documents..."):
            results = st.session_state.db.query(question, n_results=10)

        if not results or not results['documents'][0]:
            return None, []

        # Filter by similarity
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results.get('distances', [[0] * len(documents)])[0]

        filtered_chunks = []
        filtered_metas = []
        filtered_sims = []

        for doc, meta, distance in zip(documents, metadatas, distances):
            similarity = max(0, 100 * (1 - distance / 2))
            if similarity >= min_similarity:
                filtered_chunks.append(doc)
                filtered_metas.append(meta)
                filtered_sims.append(similarity)

        if not filtered_chunks:
            return None, []

        # Generate answer with LLM
        with st.spinner("Generating answer..."):
            answer = st.session_state.llm.generate_answer(
                question,
                filtered_chunks[:n_results],
                filtered_metas[:n_results]
            )

        return answer, list(zip(filtered_chunks[:n_results],
                               filtered_metas[:n_results],
                               filtered_sims[:n_results]))

    except Exception as e:
        st.error(f"Error querying RAG: {str(e)}")
        return None, []


# Main UI
st.title("📚 RAG Document Q&A System")
st.markdown("Ask questions about your documents and get AI-powered answers")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    # LLM Provider
    llm_provider = st.selectbox(
        "LLM Provider",
        options=['anthropic', 'openai', 'ollama'],
        index=0,
        help="Choose which LLM to use for answers"
    )

    if llm_provider != st.session_state.get('llm_provider'):
        st.session_state.llm_provider = llm_provider
        st.session_state.llm = None  # Reset LLM

    # Similarity threshold
    min_similarity = st.slider(
        "Minimum Similarity (%)",
        min_value=0,
        max_value=100,
        value=60,
        step=5,
        help="Only show results above this similarity threshold"
    )

    # Number of chunks
    n_chunks = st.slider(
        "Context Chunks",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of document chunks to use for context"
    )

    st.divider()

    # Database stats
    if st.session_state.db:
        stats = st.session_state.db.get_collection_stats()
        st.metric("Document Chunks", stats['document_count'])

    # Clear history
    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.rerun()

# Initialize RAG
if not initialize_rag():
    st.stop()

# Query input
question = st.text_input(
    "Ask a question about your documents:",
    placeholder="What are the main findings?",
    key="question_input"
)

# Search button
if st.button("🔍 Search", type="primary") or question:
    if question:
        # Query RAG
        answer, sources = query_rag(question, min_similarity, n_chunks)

        if answer:
            # Add to history
            st.session_state.history.insert(0, {
                'question': question,
                'answer': answer,
                'sources': sources
            })

            # Display answer
            st.markdown("### 💬 Answer")
            st.markdown(answer)

            # Display sources
            if sources:
                st.markdown("### 📄 Sources")
                for i, (chunk, meta, sim) in enumerate(sources, 1):
                    with st.expander(
                        f"[{i}] {meta.get('filename', 'Unknown')} "
                        f"(Chunk {meta.get('chunk_index', 0) + 1}) - "
                        f"{sim:.1f}% similarity"
                    ):
                        st.markdown(chunk)
        else:
            st.warning("No relevant results found. Try lowering the similarity threshold or rephrasing your question.")

# Display history
if st.session_state.history:
    st.divider()
    st.markdown("## 📜 Query History")

    for i, item in enumerate(st.session_state.history):
        with st.expander(f"Q: {item['question']}", expanded=(i == 0)):
            st.markdown("**Answer:**")
            st.markdown(item['answer'])

            if item['sources']:
                st.markdown("**Sources:**")
                for j, (chunk, meta, sim) in enumerate(item['sources'], 1):
                    st.caption(
                        f"[{j}] {meta.get('filename', 'Unknown')} "
                        f"(Chunk {meta.get('chunk_index', 0) + 1}) - {sim:.1f}%"
                    )

# Footer
st.divider()
st.caption("Powered by ChromaDB + Sentence Transformers + Claude/GPT")
