# Complete RAG System Guide

Your system now has **full RAG capabilities** - it can answer questions in natural language using your documents!

## 🎯 How It Works

```
1. You ask: "What are the key findings about climate change?"
                    ↓
2. Vector DB finds relevant chunks from your PDFs
                    ↓
3. LLM reads those chunks + your question
                    ↓
4. LLM generates: "Based on the documents, the key findings about climate change are..."
```

## 🚀 Quick Start

### Step 1: Get an API Key

Choose ONE of these options:

**Option A: Anthropic Claude (Recommended)**
- Sign up: https://console.anthropic.com/
- Get API key from: Settings → API Keys
- Cost: ~$0.003 per query (very cheap)

**Option B: OpenAI GPT**
- Sign up: https://platform.openai.com/
- Get API key from: API Keys section
- Cost: ~$0.001 per query

**Option C: Ollama (FREE, Local)**
- Install: https://ollama.ai/download
- Run: `ollama pull llama3.2` then `ollama serve`
- Cost: FREE (runs on your computer)

### Step 2: Set Your API Key

Create a `.env` file in your project root:

```bash
# Copy the example file
cp .env.example .env

# Edit it with your API key
nano .env
```

Add your key:
```bash
# For Anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# OR for OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# OR use Ollama (no key needed)
```

### Step 3: Run the RAG CLI

```bash
source venv/bin/activate
python -m src.cli.query_cli
```

You'll see:
```
Setup LLM for Answers (Optional)
Do you want natural language answers? (Requires API key)
1. Anthropic Claude (recommended)
2. OpenAI GPT
3. Ollama (local, free, requires Ollama installed)
4. Skip (just show matching chunks)

Choose (1-4): 1
```

## 💬 Example Session

```bash
Query> What are the main topics discussed in the documents?

Generating answer...

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Answer                                              ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                     ┃
┃ Based on the provided documents, the main topics   ┃
┃ discussed include:                                  ┃
┃                                                     ┃
┃ 1. **Machine Learning Algorithms** [1] - The       ┃
┃    documents cover various ML techniques including  ┃
┃    supervised and unsupervised learning methods.    ┃
┃                                                     ┃
┃ 2. **Data Processing** [2] - Several sections      ┃
┃    discuss data cleaning, normalization, and        ┃
┃    feature engineering approaches.                  ┃
┃                                                     ┃
┃ 3. **Model Evaluation** [3] - The documents        ┃
┃    explain different metrics for assessing model    ┃
┃    performance such as accuracy and F1-score.       ┃
┃                                                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Sources used:
  [1] ml_guide.pdf (Chunk 5)
  [2] data_handbook.pdf (Chunk 12)
  [3] evaluation_methods.pdf (Chunk 3)
```

## 🎮 CLI Commands

| Command | Description |
|---------|-------------|
| `<question>` | Ask any question about your documents |
| `mode answer` | Switch to answer mode (natural language) |
| `mode chunks` | Switch to chunk mode (show raw chunks) |
| `threshold 80` | Set minimum similarity to 80% |
| `stats` | Show database statistics |
| `exit` | Exit the CLI |

## 📊 Two Modes

### Answer Mode (Default with LLM)
Get natural language answers:
```
Query> How does machine learning work?

Answer: Machine learning works by training algorithms on data
to identify patterns...
```

### Chunk Mode (Original)
See the raw document chunks:
```
Query> machine learning

┃ Rank ┃ Similarity ┃ Source      ┃ Chunk ┃ Preview
┃ 1    ┃ 95.2%      ┃ guide.pdf   ┃ 3/12  ┃ Machine learning is...
```

Switch with: `mode chunks` or `mode answer`

## 💡 Tips for Better Answers

### ✅ Good Questions
- "What are the key findings about X?"
- "Explain how Y works according to the documents"
- "Summarize the methodology used"
- "What are the differences between A and B?"

### ❌ Avoid
- Single words: "machine learning" → Ask "What is machine learning?"
- Too vague: "Tell me about the docs" → Be specific
- Outside document scope: "What's the weather?" → Only asks about your PDFs

## 🔧 Troubleshooting

### "Error generating answer with Anthropic: 401"
- Check your API key in `.env`
- Make sure it starts with `sk-ant-`
- Verify you have credits: https://console.anthropic.com/

### "Error: Ollama returned status 404"
- Install Ollama: https://ollama.ai/
- Pull model: `ollama pull llama3.2`
- Start server: `ollama serve`

### "No results found"
- Lower threshold: `threshold 50`
- Try different wording
- Make sure PDFs were processed: `python process_pdfs.py --reset`

## 💰 Cost Comparison

| Provider | Cost/Query | Quality | Speed |
|----------|-----------|---------|-------|
| **Anthropic Claude** | ~$0.003 | Excellent | Fast |
| **OpenAI GPT-4o-mini** | ~$0.001 | Very Good | Fast |
| **Ollama (local)** | FREE | Good | Medium |

**Example:** 1000 queries = $3 with Anthropic, $1 with OpenAI, FREE with Ollama

## 🎯 Complete Workflow

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Add PDFs (if not done)
cp ~/Documents/*.pdf data/pdfs/

# 3. Process PDFs
python process_pdfs.py --reset

# 4. Set API key
echo 'ANTHROPIC_API_KEY=your_key_here' > .env

# 5. Start RAG CLI
python -m src.cli.query_cli

# 6. Choose LLM provider (1 for Anthropic)

# 7. Ask questions!
Query> What are the main conclusions?
```

## 🆚 Answer vs Chunks Mode

**Use Answer Mode when:**
- You want direct answers to questions
- You need summaries or explanations
- You want the AI to synthesize information

**Use Chunks Mode when:**
- You want to see exact quotes from documents
- You need to verify sources
- You're doing research and need citations

## 📈 Advanced Usage

### Change LLM Model

Edit `src/backend/llm.py`:
```python
# For Anthropic
self.model = "claude-3-5-sonnet-20241022"  # Best quality
# or
self.model = "claude-3-5-haiku-20241022"   # Faster, cheaper

# For OpenAI
self.model = "gpt-4o"       # Best quality
# or
self.model = "gpt-4o-mini"  # Faster, cheaper
```

### Adjust Context Length

Edit `src/backend/llm.py`:
```python
max_tokens=1024  # Default
# Change to:
max_tokens=2048  # Longer answers
```

Happy RAG-ing! 🚀
