# Scientific Research Report: nemotron-mini:4b

**Objective**: Analyze model deviation and grounding quality shift through clinical RAG verification.

## Executive Metrics Summary
| Metric | Standard RAG | Verified RAG | Shift |
| :--- | :---: | :---: | :---: |
| **Avg Latency** | 8.24s | 28.07s | +240.7% |
| **Avg Faithfulness** | 0.26 | 0.50 | +0.24 |
| **Total PubMed Citations** | 0 | 15 | - |

### Query 1: Does the patient have any history of cancer? If so, what type?
**Verification Impact**: Significant (Lexical Similarity: 0.08)

| Feature | Standard | Verified | Delta |
| :--- | :--- | :--- | :--- |
| **Latency** | 12.33s | 24.62s | +12.29s |
| **Faithfulness** | 0.50 | 0.50 | +0.00 |
| **Hallucination** | 0.00 | 0.00 | +0.00 |

#### Clinical Deviation Analysis
- **Stability**: Verification supported existing records without significant factual shift.

---
### Query 2: Has the patient ever been prescribed Cisplatin?
**Verification Impact**: Significant (Lexical Similarity: 0.11)

| Feature | Standard | Verified | Delta |
| :--- | :--- | :--- | :--- |
| **Latency** | 5.18s | 24.37s | +19.19s |
| **Faithfulness** | 0.00 | 0.50 | +0.50 |
| **Hallucination** | 1.00 | 1.00 | +0.00 |

#### Clinical Deviation Analysis
- **Positive Correction**: PubMed verification successfully improved the grounding of the clinical response.

---
### Query 3: What are the patient's currently active medical conditions?
**Verification Impact**: Significant (Lexical Similarity: 0.08)

| Feature | Standard | Verified | Delta |
| :--- | :--- | :--- | :--- |
| **Latency** | 13.60s | 52.65s | +39.05s |
| **Faithfulness** | 0.30 | 0.50 | +0.20 |
| **Hallucination** | 0.50 | 0.50 | +0.00 |

#### Clinical Deviation Analysis
- **Positive Correction**: PubMed verification successfully improved the grounding of the clinical response.

---
### Query 4: Is there any record of a normal pregnancy for this patient?
**Verification Impact**: Significant (Lexical Similarity: 0.02)

| Feature | Standard | Verified | Delta |
| :--- | :--- | :--- | :--- |
| **Latency** | 3.35s | 16.69s | +13.33s |
| **Faithfulness** | 0.00 | 0.50 | +0.50 |
| **Hallucination** | 1.00 | 0.00 | -1.00 |

#### Clinical Deviation Analysis
- **Positive Correction**: PubMed verification successfully improved the grounding of the clinical response.

---
### Query 5: Has the patient had any suspected respiratory infections like COVID-19?
**Verification Impact**: Significant (Lexical Similarity: 0.09)

| Feature | Standard | Verified | Delta |
| :--- | :--- | :--- | :--- |
| **Latency** | 6.73s | 22.03s | +15.30s |
| **Faithfulness** | 0.50 | 0.50 | +0.00 |
| **Hallucination** | 1.00 | 0.00 | -1.00 |

#### Clinical Deviation Analysis
- **Stability**: Verification supported existing records without significant factual shift.

---
