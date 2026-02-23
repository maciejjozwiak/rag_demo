"""
LLM Integration Module
Generates natural language answers using retrieved context
"""
import os
from typing import List, Dict, Optional
from anthropic import Anthropic


class LLMAnswerGenerator:
    """Generate answers using LLM with retrieved context"""

    def __init__(self, provider: str = "anthropic", api_key: Optional[str] = None):
        """
        Initialize LLM client

        Args:
            provider: LLM provider ("anthropic", "openai", or "ollama")
            api_key: API key for the provider (not needed for ollama)
        """
        self.provider = provider.lower()

        if self.provider == "anthropic":
            self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
            self.model = "claude-3-5-sonnet-20241022"

        elif self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4o-mini"

        elif self.provider == "ollama":
            # Local Ollama - no API key needed
            import requests
            self.client = requests
            self.model = "llama3.2"
            self.ollama_url = "http://localhost:11434/api/generate"

        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'anthropic', 'openai', or 'ollama'")

    def generate_answer(self, question: str, context_chunks: List[str], metadata: List[Dict] = None) -> str:
        """
        Generate an answer using the LLM with retrieved context

        Args:
            question: User's question
            context_chunks: List of relevant text chunks from vector DB
            metadata: Optional metadata for each chunk

        Returns:
            Generated answer as string
        """
        # Build context from chunks
        context = self._format_context(context_chunks, metadata)

        # Create prompt
        prompt = self._create_prompt(question, context)

        # Generate answer based on provider
        if self.provider == "anthropic":
            return self._generate_anthropic(prompt)
        elif self.provider == "openai":
            return self._generate_openai(prompt)
        elif self.provider == "ollama":
            return self._generate_ollama(prompt)

    def _format_context(self, chunks: List[str], metadata: List[Dict] = None) -> str:
        """Format retrieved chunks into context"""
        if not chunks:
            return "No relevant information found."

        formatted = []
        for i, chunk in enumerate(chunks, 1):
            source = ""
            if metadata and i <= len(metadata):
                meta = metadata[i - 1]
                filename = meta.get('filename', 'Unknown')
                chunk_idx = meta.get('chunk_index', 0) + 1
                source = f" (Source: {filename}, Chunk {chunk_idx})"

            formatted.append(f"[{i}]{source}\n{chunk}\n")

        return "\n".join(formatted)

    def _create_prompt(self, question: str, context: str) -> str:
        """Create the prompt for the LLM"""
        return f"""You are a helpful AI assistant that answers questions based on provided documents.

Use the following context to answer the question. If the context doesn't contain enough information to answer the question, say so clearly.

CONTEXT:
{context}

QUESTION: {question}

Please provide a clear, concise answer based on the context above. If you use information from the context, you can reference the source numbers [1], [2], etc."""

    def _generate_anthropic(self, prompt: str) -> str:
        """Generate answer using Anthropic Claude"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating answer with Anthropic: {str(e)}"

    def _generate_openai(self, prompt: str) -> str:
        """Generate answer using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided documents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating answer with OpenAI: {str(e)}"

    def _generate_ollama(self, prompt: str) -> str:
        """Generate answer using local Ollama"""
        try:
            import json
            response = self.client.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            if response.status_code == 200:
                return response.json()['response']
            else:
                return f"Error: Ollama returned status {response.status_code}. Is Ollama running?"
        except Exception as e:
            return f"Error generating answer with Ollama: {str(e)}\nMake sure Ollama is installed and running: https://ollama.ai"
