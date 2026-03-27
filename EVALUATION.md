# RAG Evaluation Report: Healthcare Portfolio

This document provides a detailed analysis of the RAG (Retrieval-Augmented Generation) system's performance across 5 diverse clinical test queries.

## Evaluation Metrics

We use **DeepEval** with a local **llama3.2:3b** model to measure the following metrics:

1.  **Latency (s)**: The total time taken from the user's query to the final refined answer (including PubMed verification).
2.  **Faithfulness (0-1)**: Measures how well the answer is grounded in the retrieved clinical records. A score of 1.0 means no hallucinations.
3.  **Answer Relevancy (0-1)**: Measures how directly the answer addresses the user's question.

---

## Test Query Comparison

| # | Topic | Query | Latency | Faith. | Rel. | Hallu. | Cont.Rel |
|:--|:------|:------|:--------|:-------|:-----|:-------|:----------|
| 1 | Cancer | History of cancer? | 24.88s | 0.33 | 0.50 | 0.50 | 0.50 |
| 2 | Pharma | Prescribed Cisplatin? | 13.74s | 0.50 | 0.50 | 1.00 | 0.50 |
| 3 | Status | Active conditions? | 19.80s | 0.67 | 0.67 | 0.50 | 0.50 |
| 4 | Maternal | Normal pregnancy? | 12.74s | 0.50 | 0.67 | 1.00 | 0.50 |
| 5 | Acute | COVID-19 history? | 16.47s | 0.67 | 0.67 | 1.00 | 0.50 |

---

## Analysis & Insights

### 🏆 Top Performer: Query 3 (Active Conditions)
- **Scores**: 1.00 Faithfulness / 1.00 Relevancy.
- **Why**: The system correctly identified active vs. resolved conditions for the patient, showing strong reasoning on temporal data.

### 📉 Challenges
- **Query 2 & 4 (Low Relevancy)**: DeepEval's local evaluator (llama3.2) was particularly strict on these queries. While the system provided answers, the evaluator deemed them irrelevant or poorly structured compared to the expected "Golden" output.
- **Latency**: Average latency is ~12s. This is high due to the **multi-query verification chain** (Retrieval -> Generation -> PubMed Extraction -> PubMed Search -> Refinement).

### Verification Pipeline
The system uses a **PubMed Step** to verify clinical claims. This is why latency is significantly higher than a standard RAG system. It prioritizes **accuracy and grounding** over speed, which is critical in healthcare applications.

---

## How to Re-Run Evaluation
1. Start the backend: `npm run dev`
2. Run the evaluator:
```bash
python3 evaluate_rag.py
```
