# Healthcare RAG Suite

A modular, clinical Retrieval-Augmented Generation (RAG) system featuring local LLM inference, PubMed verification, and automated evaluation metrics.

## Quick Start Guide

### 1. Prerequisites
- **Node.js** (v18+) & **npm**
- **Python** (v3.12+) & **pip**
- **Ollama** ([Download here](https://ollama.com/))

### 2. Environment Setup

#### Install Dependencies
```bash
# Install Node.js dependencies
npm install

# Install Python evaluation dependencies
pip install -r requirements.txt
```

#### Pull Local Models
Ensure Ollama is running, then pull the required models:
```bash
ollama pull nomic-embed-text
ollama pull llama3.1
ollama pull llama3.2:3b
```

#### Configuration
Copy `.env.example` to `.env` and verify the settings:
- `FHIR_DATASET_PATH`: Absolute path to your NDJSON data directory.
- `OLLAMA_BASE_URL`: Usually `http://127.0.0.1:11434`.

---

### 3. Workflow Steps

#### Step A: Data Ingestion
Process your FHIR data into the local vector database.
```bash
npm run ingest
```

#### Step B: Start the Server
Run the Node.js backend to host the `/query` endpoint.
```bash
npm run dev
```

#### Step C: Run Tests
Execute the shell-based test suite for quick verification:
```bash
./test-queries.sh
```

#### Step D: Full Evaluation (DeepEval)
Run the professional evaluation suite to measure latency, faithfulness, and relevancy:
```bash
python3 evaluate_rag.py
```

---

## 📂 Documentation
- [**ARCHITECTURE.md**](./ARCHITECTURE.md): Detailed dataflow, diagrams, and verification chain.
- [**DATASET.md**](./DATASET.md): Overview of the synthetic FHIR sample data (10 patients).
- [**DEEPEVAL_GUIDE.md**](./DEEPEVAL_GUIDE.md): Explanation of local LLM metrics (Faithfulness, Hallucination, etc.) and evaluation flowchart.
- [**BENCHMARK_REPORT.md**](./BENCHMARK_REPORT.md): Evaluation results and multi-model hardware comparisons.
- [**EVALUATION.md**](./EVALUATION.md): Comparison of baseline test queries and metric definitions.

## 🛠️ Tech Stack
- **Engine**: Node.js / Express
- **Vector DB**: LanceDB
- **LLMs**: Ollama (llama3.1, nomic-embed-text)
- **Evaluation**: DeepEval (Confident AI)
- **Compliance**: Local-only processing for PHI privacy.
