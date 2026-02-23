# Vector Database Explained - What's Actually Stored

## 🎯 Quick Answer

**Your `vector_db/` folder IS the database. No server needed!**

```
vector_db/
├── chroma.sqlite3              # Document text + metadata (SQL database)
└── [uuid-folders]/             # Vector embeddings (binary files)
    ├── data_level0.bin         # The actual 384-dimensional vectors
    ├── link_lists.bin          # HNSW graph (for fast search)
    ├── length.bin              # Index sizes
    └── header.bin              # Index metadata
```

##  2 Types of ChromaDB Modes

### ❌ Server Mode (What you DON'T have)
```
Your App → Network → ChromaDB Server (running on port 8000)
                          ↓
                   Stores data in files
```
**Requires:** `chroma run --host localhost --port 8000`

### ✅ Persistent/Embedded Mode (What you HAVE)
```
Your App → Directly reads/writes vector_db/ files
```
**Requires:** Nothing! Just the folder.

This is like SQLite vs PostgreSQL:
- **PostgreSQL** = Server (always running)
- **SQLite** = File-based (your app opens the .db file)
- **ChromaDB Persistent** = File-based (like SQLite)

## 📦 What's Actually Stored

### 1. Document Text & Metadata (chroma.sqlite3)
```sql
-- SQLite database contains:
CREATE TABLE embeddings (
    id TEXT,              -- "cholas.pdf_chunk_0"
    document TEXT,        -- "The Chola Dynasty was..."
    metadata JSON         -- {"filename": "cholas.pdf", "chunk_index": 0}
);
```

You can even inspect it:
```bash
sqlite3 vector_db/chroma.sqlite3 "SELECT * FROM embeddings LIMIT 1;"
```

### 2. Vector Embeddings (*.bin files)
```
Each document chunk → 384 floating point numbers

Example:
"The Chola Dynasty" →
[-0.0517, -0.0035, 0.0035, 0.0046, -0.0977, -0.0322, ...]
                     ↑
                384 numbers total
```

These are stored in **data_level0.bin** as raw binary data.

### 3. HNSW Index (link_lists.bin)
```
Graph structure for fast search:

  Chunk 1 ← connected to → Chunk 5
      ↓                         ↓
  Chunk 3 ← connected to → Chunk 8
      ↓                         ↓
     ...                       ...
```

This allows O(log N) search instead of O(N).

## 🔬 Inspect Your Database

Run the inspection script:
```bash
python inspect_vectordb.py
```

You'll see:
- Total chunks stored
- Sample documents
- Actual vector embeddings
- File sizes
- Documents per PDF

## 📊 Example from YOUR Database

From the inspection:
```
Collection: pdf_documents
Total Chunks: 6
Source: cholas.pdf

Chunk 1: "The Chola Dynasty: An Overview..."
  → Stored as 384-dim vector: [-0.0517, -0.0035, ...]
  → Size: ~1.5 KB per chunk

Chunk 2: "golden age began during the reign..."
  → Stored as 384-dim vector: [-0.0421, 0.0213, ...]
  → Size: ~1.5 KB per chunk
```

## 💾 File Sizes

For your 6 chunks (1 PDF):
- `chroma.sqlite3`: ~316 KB (document text + metadata)
- `data_level0.bin`: ~10 KB (vectors: 6 chunks × 384 floats × 4 bytes)
- `link_lists.bin`: ~5 KB (HNSW graph)
- **Total: ~330 KB**

**Scaling:**
- 100 chunks ≈ 3 MB
- 1,000 chunks ≈ 30 MB
- 10,000 chunks ≈ 300 MB

## 🚀 Why No Server Needed?

**When app starts:**
```python
from src.backend.vectorize import VectorDB

db = VectorDB()  # Opens vector_db/ files directly
                 # No network, no server!

results = db.query("question")  # Reads from files
```

**ChromaDB's PersistentClient:**
```python
self.client = chromadb.PersistentClient(path="./vector_db")
#                        ↑
#                  Just reads/writes files!
```

## 🌐 What Happens When You Deploy?

### Option 1: Include vector_db/ folder
```bash
# Push to GitHub
git add vector_db/
git push

# Deploy to Streamlit/Railway/etc
# App reads vector_db/ directly
```

### Option 2: Re-build on deployment
```bash
# Don't include vector_db/
# On first run:
if not exists("vector_db"):
    run("python process_pdfs.py")
```

### Option 3: Use ChromaDB Server (production)
```bash
# Start ChromaDB server
docker run -p 8000:8000 chromadb/chroma

# App connects to server
client = chromadb.HttpClient(host="localhost", port=8000)
```

## 🔍 Comparing to Other Databases

| Database | Storage | Server Needed? | Your System |
|----------|---------|----------------|-------------|
| **SQLite** | .db file | ❌ No | Similar! |
| **PostgreSQL** | Files | ✅ Yes | Different |
| **ChromaDB (Persistent)** | Files | ❌ No | **This is you** |
| **ChromaDB (Server)** | Files | ✅ Yes | Not you |
| **Pinecone** | Cloud | ✅ Yes | Different |

## 🎯 Key Takeaways

1. ✅ **vector_db/ IS the database** (like a .db file)
2. ✅ **No server needed** (embedded mode)
3. ✅ **Just files** (portable, easy to deploy)
4. ✅ **Include in Git** (< 100MB) or use Git LFS
5. ✅ **Works online** (Streamlit/Railway read files directly)

## 🧪 Try These Commands

### See what's inside:
```bash
# Inspect the database
python inspect_vectordb.py

# Check file sizes
du -sh vector_db/*

# Count chunks
python -c "from src.backend.vectorize import VectorDB; db = VectorDB(); print(db.collection.count())"

# View SQLite contents
sqlite3 vector_db/chroma.sqlite3 ".tables"
```

### Test a query:
```python
from src.backend.vectorize import VectorDB

db = VectorDB()
results = db.query("Chola Dynasty", n_results=3)

for doc in results['documents'][0]:
    print(doc[:100])
```

## ❓ Common Questions

**Q: Do I need to install ChromaDB server?**
A: No! You're using persistent mode (file-based).

**Q: Can multiple people use it at once?**
A: Locally, no (file locks). Online deployment, yes (each user gets their own connection).

**Q: Is it safe to delete vector_db/?**
A: Only if you can re-run `python process_pdfs.py` to rebuild it!

**Q: How do I backup?**
A: Just copy the entire `vector_db/` folder!

**Q: Can I view the vectors?**
A: Yes! Run `python inspect_vectordb.py`

## 🔗 Further Reading

- ChromaDB Persistent Client: https://docs.trychroma.com/usage-guide#persistent-client
- SQLite vs Server DBs: https://sqlite.org/whentouse.html
- HNSW Algorithm: https://arxiv.org/abs/1603.09320
