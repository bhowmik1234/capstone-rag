# Scientific Research Report: llama3.2:3b

**Objective**: Analyze model deviation and grounding quality shift through clinical RAG verification.

## Executive Metrics Summary
| Metric | Standard RAG | Verified RAG | Shift |
| :--- | :---: | :---: | :---: |
| **Avg Latency** | 15.71s | 35.62s | +126.8% |
| **Avg Faithfulness** | 0.50 | 0.68 | +0.17 |
| **Total PubMed Citations** | 0 | 15 | - |

### Query 1: Does the patient have any history of cancer? If so, what type?
**Verification Impact**: Significant (Lexical Similarity: 0.14)

| Feature | Standard | Verified | Delta |
| :--- | :--- | :--- | :--- |
| **Latency** | 21.51s | 38.25s | +16.74s |
| **Faithfulness** | 0.29 | 0.83 | +0.55 |
| **Hallucination** | 0.00 | 0.00 | +0.00 |

#### Clinical Deviation Analysis
- **Positive Correction**: PubMed verification successfully improved the grounding of the clinical response.

---
### Query 2: Has the patient ever been prescribed Cisplatin?
**Verification Impact**: Significant (Lexical Similarity: 0.05)

| Feature | Standard | Verified | Delta |
| :--- | :--- | :--- | :--- |
| **Latency** | 17.39s | 30.88s | +13.49s |
| **Faithfulness** | 0.43 | 0.56 | +0.13 |
| **Hallucination** | 1.00 | 1.00 | +0.00 |

#### Clinical Deviation Analysis
- **Positive Correction**: PubMed verification successfully improved the grounding of the clinical response.

---
### Query 3: What are the patient's currently active medical conditions?
**Verification Impact**: Significant (Lexical Similarity: 0.17)

| Feature | Standard | Verified | Delta |
| :--- | :--- | :--- | :--- |
| **Latency** | 15.01s | 40.13s | +25.13s |
| **Faithfulness** | 0.57 | 1.00 | +0.43 |
| **Hallucination** | 0.50 | 0.50 | +0.00 |

#### Clinical Deviation Analysis
- **Positive Correction**: PubMed verification successfully improved the grounding of the clinical response.

---
### Query 4: Is there any record of a normal pregnancy for this patient?
**Verification Impact**: Significant (Lexical Similarity: 0.09)

| Feature | Standard | Verified | Delta |
| :--- | :--- | :--- | :--- |
| **Latency** | 11.80s | 29.12s | +17.31s |
| **Faithfulness** | 0.57 | 0.46 | -0.11 |
| **Hallucination** | 1.00 | 1.00 | +0.00 |

#### Clinical Deviation Analysis
- **Context Contamination**: External verification introduced conflicting or generalized info that reduced patient-specific faithfulness.

---
### Query 5: Has the patient had any suspected respiratory infections like COVID-19?
**Verification Impact**: Significant (Lexical Similarity: 0.18)

| Feature | Standard | Verified | Delta |
| :--- | :--- | :--- | :--- |
| **Latency** | 12.82s | 39.70s | +26.88s |
| **Faithfulness** | 0.67 | 0.55 | -0.12 |
| **Hallucination** | 1.00 | 1.00 | +0.00 |

#### Clinical Deviation Analysis
- **Context Contamination**: External verification introduced conflicting or generalized info that reduced patient-specific faithfulness.

---
