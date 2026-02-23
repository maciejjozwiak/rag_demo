# How Vector Search Works in Your RAG System

## 🎯 The Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ INDEXING (Done once when you run process_pdfs.py)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PDF Document                                                   │
│      ↓                                                          │
│  Extract Text → "Machine learning is..."                       │
│      ↓                                                          │
│  Split into Chunks → ["Machine learning is...", "Neural..."]   │
│      ↓                                                          │
│  Generate Embeddings:                                           │
│      "Machine learning is..." → [0.23, -0.45, 0.89, ...]      │
│      "Neural networks..." → [0.21, -0.47, 0.85, ...]           │
│      ↓                                                          │
│  Store in ChromaDB:                                             │
│      ┌──────────┬─────────────────┬──────────────────┐         │
│      │ Chunk ID │ Text            │ Vector (384-dim) │         │
│      ├──────────┼─────────────────┼──────────────────┤         │
│      │ chunk_1  │ "Machine..."    │ [0.23, -0.45...] │         │
│      │ chunk_2  │ "Neural..."     │ [0.21, -0.47...] │         │
│      └──────────┴─────────────────┴──────────────────┘         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ QUERYING (Every time you ask a question)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Your Question: "What is ML?"                                   │
│      ↓                                                          │
│  [1] Convert to Vector                                          │
│      "What is ML?" → [0.24, -0.44, 0.88, ...] (384 numbers)    │
│      ↓                                                          │
│  [2] ChromaDB compares with ALL stored vectors                  │
│      Query vector vs chunk_1 vector → Similarity: 0.95         │
│      Query vector vs chunk_2 vector → Similarity: 0.82         │
│      Query vector vs chunk_3 vector → Similarity: 0.45         │
│      ... (compares with all 145 chunks in ~10ms)               │
│      ↓                                                          │
│  [3] Rank by similarity                                         │
│      1. chunk_1 (95%)                                           │
│      2. chunk_2 (82%)                                           │
│      3. chunk_5 (74%)                                           │
│      ↓                                                          │
│  [4] Filter by threshold (60%)                                  │
│      ✓ chunk_1 (95%) - PASS                                    │
│      ✓ chunk_2 (82%) - PASS                                    │
│      ✓ chunk_5 (74%) - PASS                                    │
│      ✗ chunk_8 (45%) - FILTERED OUT                            │
│      ↓                                                          │
│  [5] Return top results                                         │
│      ["Machine learning is...", "Neural networks..."]          │
└─────────────────────────────────────────────────────────────────┘
```

## 📐 The Math Behind It

### 1. **Text → Numbers (Embeddings)**

The `all-MiniLM-L6-v2` model converts text to 384-dimensional vectors:

```python
# Your query
"What is machine learning?"
    ↓
[0.234, -0.456, 0.891, ..., 0.123]  # 384 numbers
```

### 2. **Similarity Calculation (Cosine Similarity)**

Measures the angle between two vectors:

```python
def cosine_similarity(vec1, vec2):
    dot_product = vec1 · vec2
    magnitude = ||vec1|| × ||vec2||
    return dot_product / magnitude
```

**Results:**
- `1.0` = Identical meaning
- `0.8-0.9` = Very similar
- `0.5-0.7` = Somewhat related
- `0.0` = Unrelated
- `-1.0` = Opposite meaning

### 3. **Why It Works**

Words with similar meanings are placed **near each other** in vector space:

```
Vector Space (simplified to 2D):

    "neural networks" ●
                      ↑ (close = similar)
    "machine learning" ●

    (far away)
         ↓
    "weather forecast" ●
```

## 🔬 Real Example

Let's trace a query through the system:

### Query: "How does AI work?"

**Step 1: Embed Query**
```
"How does AI work?" → [0.45, -0.23, 0.67, ..., 0.89]
```

**Step 2: Documents in ChromaDB**
```
Doc A: "Artificial intelligence learns from data"
       Vector: [0.47, -0.25, 0.65, ..., 0.87]

Doc B: "Neural networks process information"
       Vector: [0.43, -0.21, 0.69, ..., 0.85]

Doc C: "The recipe calls for 2 cups of flour"
       Vector: [-0.12, 0.67, -0.34, ..., 0.23]
```

**Step 3: Calculate Similarities**
```
cosine(query, Doc A) = 0.94  → 94% similar ✅
cosine(query, Doc B) = 0.87  → 87% similar ✅
cosine(query, Doc C) = 0.12  → 12% similar ❌
```

**Step 4: Return Top Results**
```
1. Doc A (94%) - "Artificial intelligence learns from data"
2. Doc B (87%) - "Neural networks process information"
```

**Note:** Doc A is #1 even though it says "artificial intelligence" not "AI"!

## 🎨 Visual Representation

Imagine each piece of text as a point in 384-dimensional space:

```
Similar meanings cluster together:

    ┌─ ML Cluster ─────────────┐
    │  ● "machine learning"     │
    │  ● "neural networks"      │
    │  ● "deep learning"        │
    │  ● "AI algorithms"        │
    └───────────────────────────┘

    ┌─ Programming Cluster ────┐
    │  ● "Python code"          │
    │  ● "JavaScript"           │
    │  ● "programming"          │
    └───────────────────────────┘

    ┌─ Weather Cluster ────────┐
    │  ● "rain forecast"        │
    │  ● "temperature"          │
    └───────────────────────────┘

When you query "What is ML?", the system finds the
point closest to your query in this space.
```

## ⚡ What Happens in Your Code

### In `vectorize.py`:

```python
# When you call db.query()
results = self.collection.query(
    query_texts=[query_text],  # Your question
    n_results=n_results,       # How many results
    include=["documents", "metadatas", "distances"]
)
```

### ChromaDB does this internally:

1. **Embeds your query** using the same model that embedded the documents
2. **Computes cosine distance** to every stored vector (uses HNSW index for speed)
3. **Sorts by distance** (smaller distance = more similar)
4. **Returns top N** results with their distances

### Distance → Similarity Conversion:

ChromaDB returns **distance** (0 = perfect match, 2 = opposite):

```python
# In your CLI (query_cli.py)
similarity = max(0, 100 * (1 - distance / 2))

# Examples:
distance = 0.0  → similarity = 100%  (identical)
distance = 0.4  → similarity = 80%   (very similar)
distance = 1.0  → similarity = 50%   (somewhat similar)
distance = 2.0  → similarity = 0%    (opposite)
```

## 🚀 Why This Is Fast

**Question:** How can it compare your query to 10,000 document chunks in milliseconds?

**Answer:** HNSW (Hierarchical Navigable Small World) Index

Instead of checking every vector:
```
❌ Slow (Linear Search): Check all 10,000 vectors
✅ Fast (HNSW Index): Check ~log(N) vectors

For 10,000 chunks:
  - Linear: 10,000 comparisons
  - HNSW: ~13 comparisons
```

It's like a tree structure that navigates to similar vectors quickly.

## 🧪 Try It Yourself

Run the demo script to see this in action:

```bash
source venv/bin/activate
python explain_retrieval.py
```

This will show you:
- Actual embeddings for sample queries
- Similarity scores between your query and different documents
- Why some documents rank higher than others

## 💡 Key Takeaways

1. **Everything becomes numbers** (384-dimensional vectors)
2. **Similar meanings = similar vectors** (close together in space)
3. **Cosine similarity** measures how similar vectors are
4. **No exact keyword needed** - it's all about semantic meaning
5. **HNSW index** makes it lightning fast even with millions of chunks

## 🔗 References

- **Sentence-Transformers**: https://www.sbert.net/
- **ChromaDB**: https://docs.trychroma.com/
- **HNSW Algorithm**: https://arxiv.org/abs/1603.09320
- **Cosine Similarity**: https://en.wikipedia.org/wiki/Cosine_similarity
