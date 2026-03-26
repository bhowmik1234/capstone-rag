# Healthcare RAG Backend

A production-style clinical question-answering system using Node.js, Express, LanceDB, and Ollama.

## Setup

1. **Prerequisites**
   - Node.js (v18+)
   - Ollama (running locally)
   - Pulled models: `nomic-embed-text` and `llama3.1`
     ```bash
     ollama pull nomic-embed-text
     ollama pull llama3.1
     ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Configure Environment**
   Check `.env` and ensure `FHIR_DATASET_PATH` points to your FHIR NDJSON files.

4. **Ingest Data**
   Run the ingestion pipeline to normalize FHIR data and populate the local vector database.
   ```bash
   npm run ingest
   ```

5. **Start Server**
   ```bash
   npm run dev
   ```

## API Usage

### Query Clinical Records
**POST** `/query`

**Payload:**
```json
{
  "question": "What are the patient's current vitals?",
  "patientId": "e305e608-f1c7-43f1-b4e6-d703fac1b033"
}
```

**Example Curl:**
```bash
curl -X POST http://localhost:3000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the latest blood pressure for this patient?", "patientId": "e305e608"}'
```

## Features
- **Resource-Aware Chunking**: Treats each FHIR resource as an atomic semantic unit.
- **Clinical Grounding**: System prompt enforces zero hallucination and strict adherence to evidence.
- **Local Everything**: No external APIs used; runs fully offline.
- **Provenancel**: Every answer includes the source resource type, ID, and date.
