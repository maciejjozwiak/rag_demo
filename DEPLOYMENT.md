# Deployment Guide - Make Your RAG System Online

## 🚀 Three Deployment Options

### Option 1: Streamlit Cloud (FREE & EASIEST - 5 minutes)
### Option 2: Railway/Render (Easy - 10 minutes)
### Option 3: Docker + VPS (Full control - 30 minutes)

---

## 🎯 Option 1: Streamlit Cloud (Recommended for Quick Deploy)

**Pros:** FREE, No server setup, SSL included, Takes 5 minutes
**Cons:** Public (unless you pay), Limited resources (1GB RAM)

### Step 1: Test Locally First

```bash
# Make sure it works locally
source venv/bin/activate
streamlit run app.py

# Visit http://localhost:8501
```

### Step 2: Push to GitHub

```bash
# Initialize git if not already
git init
git add .
git commit -m "Initial RAG app"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/rag-demo.git
git push -u origin main
```

### Step 3: Deploy to Streamlit Cloud

1. Go to: https://share.streamlit.io/
2. Click "New app"
3. Select your GitHub repo
4. Set:
   - **Main file**: `app.py`
   - **Python version**: 3.12
5. Click "Advanced settings"
6. Add secrets (your API keys):
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-xxxxx"
   # OR
   OPENAI_API_KEY = "sk-xxxxx"
   ```
7. Click "Deploy"!

**That's it!** Your app will be live at:
`https://YOUR_USERNAME-rag-demo.streamlit.app`

### Important Notes:
- ⚠️ **Upload vector_db folder** - Your docs need to be indexed first
- ⚠️ **Large files** - GitHub has 100MB limit, use Git LFS for big DBs
- ⚠️ **Free tier** - 1GB RAM, might restart if inactive

---

## 🎯 Option 2: Railway (Easy + More Power)

**Pros:** More resources, Private, Custom domain, $5/month
**Cons:** Not free, Need credit card

### Step 1: Create Railway Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init
```

### Step 2: Add Configuration

Create `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run app.py --server.port $PORT",
    "healthcheckPath": "/_stcore/health"
  }
}
```

### Step 3: Set Environment Variables

```bash
railway variables set ANTHROPIC_API_KEY=sk-ant-xxxxx
railway variables set OPENAI_API_KEY=sk-xxxxx
```

### Step 4: Deploy

```bash
railway up
```

Your app will be at: `https://your-app.up.railway.app`

**Cost:** ~$5-10/month

---

## 🎯 Option 3: FastAPI Backend + HTML Frontend (Most Flexible)

For more control, deploy as an API:

### Create FastAPI Backend

Create `api.py`:
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.backend.vectorize import VectorDB
from src.backend.llm import LLMAnswerGenerator
import os

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG
db = VectorDB()
llm = LLMAnswerGenerator(
    provider=os.getenv("LLM_PROVIDER", "anthropic")
)

class Query(BaseModel):
    question: str
    min_similarity: float = 60.0
    n_results: int = 5

@app.post("/api/query")
async def query_rag(query: Query):
    try:
        # Get relevant chunks
        results = db.query(query.question, n_results=10)

        # Filter by similarity
        # ... (filtering logic)

        # Generate answer
        answer = llm.generate_answer(
            query.question,
            filtered_chunks,
            filtered_metas
        )

        return {
            "answer": answer,
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}
```

Deploy to:
- **Fly.io**: `fly launch` (Easy, $3/month)
- **Render**: Connect GitHub (Easy, $7/month)
- **AWS/GCP**: More complex but scalable

---

## 🐳 Option 4: Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose port
EXPOSE 8501

# Run
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run

```bash
# Build
docker build -t rag-app .

# Run locally
docker run -p 8501:8501 \
  -e ANTHROPIC_API_KEY=sk-ant-xxx \
  rag-app

# Visit http://localhost:8501
```

### Deploy to:
- **Fly.io**: `fly launch`
- **Railway**: `railway up`
- **DigitalOcean**: Deploy from Docker registry

---

## 📦 What You Need to Upload

### Essential Files:
```
✅ app.py
✅ requirements.txt
✅ src/ (entire folder)
✅ vector_db/ (your indexed documents!)
✅ .streamlit/config.toml
```

### DON'T Upload:
```
❌ venv/
❌ __pycache__/
❌ .env (use platform secrets instead)
❌ data/pdfs/ (too large, already indexed)
```

---

## 🔒 Security Best Practices

### 1. **Never Commit API Keys**
```bash
# .gitignore
.env
*.key
secrets/
```

### 2. **Use Platform Secrets**
- Streamlit: Settings → Secrets
- Railway: `railway variables set`
- Render: Environment tab

### 3. **Add Authentication (Optional)**
```python
# In app.py
import streamlit_authenticator as stauth

# Add login
authenticator = stauth.Authenticate(...)
name, authentication_status, username = authenticator.login()

if not authentication_status:
    st.stop()
```

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid | Custom Domain | Private |
|----------|-----------|------|---------------|---------|
| **Streamlit Cloud** | ✅ 1GB RAM | $20/mo unlimited | ❌ | Premium only |
| **Railway** | $5 credit | $5-20/mo | ✅ | ✅ |
| **Render** | 750hrs/mo | $7/mo | ✅ | ✅ |
| **Fly.io** | Small apps | $3-10/mo | ✅ | ✅ |
| **Heroku** | ❌ | $7/mo | ✅ | ✅ |

**Plus:** LLM API costs (~$0.003/query)

---

## 🚨 Important: Vector Database Upload

Your `vector_db/` folder contains your indexed documents:

### Small DB (<100MB):
```bash
# Just commit to Git
git add vector_db/
git commit -m "Add vector database"
git push
```

### Large DB (>100MB):
**Option A: Git LFS**
```bash
# Install Git LFS
git lfs install
git lfs track "vector_db/*"
git add .gitattributes
git commit -m "Track vector DB with LFS"
```

**Option B: Object Storage**
```bash
# Upload to S3/GCS/etc
# Download on server startup
```

**Option C: Re-index on Deploy**
```bash
# Add to startup:
if not os.path.exists("vector_db"):
    run_processing_script()
```

---

## ✅ Quick Deploy Checklist

- [ ] Test locally: `streamlit run app.py`
- [ ] Commit to GitHub
- [ ] Add vector_db/ folder
- [ ] Choose platform (Streamlit Cloud = easiest)
- [ ] Add API keys as secrets
- [ ] Deploy!
- [ ] Test online URL
- [ ] Share with others

---

## 🎓 Recommended Path

**For Learning/Personal:**
→ Streamlit Cloud (FREE)

**For Small Team:**
→ Railway ($5/mo)

**For Production:**
→ FastAPI + Fly.io/Render ($10-20/mo)

**For Enterprise:**
→ AWS/GCP with Docker + Load Balancer

---

## 🔗 Helpful Links

- Streamlit Deployment: https://docs.streamlit.io/deploy
- Railway Docs: https://docs.railway.app/
- Render Docs: https://render.com/docs
- Fly.io Docs: https://fly.io/docs/
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/

Start with Streamlit Cloud - it's the fastest way to get online! 🚀
