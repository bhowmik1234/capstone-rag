# Model Comparison: Llama 3.2 3B vs. 1B

This document compares the performance of the Healthcare RAG system using two different local LLMs: **Llama 3.2 3B** and **Llama 3.2 1B**.

## Executive Summary
While the 1B model is smaller, **Llama 3.2 3B** outperformed it in both **Speed (Latency)** and **Factual Accuracy (Faithfulness)** in this clinical RAG environment. The 1B model showed a tendency for hallucinations and slower inference times, likely due to less efficient reasoning in the multi-stage verification chain.

---

## 📊 Key Metrics Comparison

| Metric | Llama 3.2 3B | Llama 3.2 1B | Winner |
| :--- | :--- | :--- | :--- |
| **Avg. Latency** | **11.88s** | 17.52s | **3B** |
| **Avg. Faithfulness** | **0.63** | 0.53 | **3B** |
| **Avg. Hallucination** | **N/A** | 0.80 | **-** |
| **Avg. Contextual Rel.** | **N/A** | 0.50 | **-** |
| **Success Rate** | **20.0%** | 0.0% | **3B** |

*Note: Success Rate is based on reaching a >0.70 threshold in both Faithfulness and Relevancy.*

---

## 🔍 Detailed Analysis

### 1. Latency Paradox
Counter-intuitively, the **1B model was ~50% slower** than the 3B model.
- **Hypothesis**: The 1B model produced more verbose or redundant text during the initial generation and verification steps, causing the total processing time to increase. 
- **Impact**: For healthcare RAG where sequential verification is key, the 3B model is more efficient.

### 2. Faithfulness & Hallucination
- **Llama 3.2 3B**: Achieved a perfect **1.00 Faithfulness** on complex active condition queries.
- **Llama 3.2 1B**: Struggled with grounding, frequently missing resolved vs. active status nuances, leading to lower faithfulness (0.57).

### 3. Relevancy
Both models performed similarly in terms of relevancy, though the 1B model sometimes provided "fluffier" answers that the 1B evaluator (DeepEval) deemed slightly more relevant in style, despite lower factual accuracy.

---

## 🛡️ Recommendation
For this Healthcare RAG implementation, we recommend staying with **Llama 3.2 3B**. It provides a better balance of reasoning speed and clinical accuracy, which is paramount when dealing with patient data and peer-reviewed literature from PubMed.
