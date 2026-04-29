# Comprehensive Clinical RAG Benchmark Report

## Executive Summary
This report evaluates the performance of three state-of-the-art Large Language Models (LLMs) integrated into a clinical Retrieval-Augmented Generation (RAG) system. The models were tested across two workflows: **Standard RAG** (retrieval from patient records) and **Verified RAG** (retrieval from patient records + live PubMed verification).

| Model | Avg Latency (Std) | Avg Latency (Ver) | Avg Faithfulness (Std) | Avg Faithfulness (Ver) | Clinical Improvement |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Llama 3.2 (3B)** | 15.71s | 35.62s | 0.50 | **0.68** | **+36%** |
| **Meditron (7B)** | 14.42s | 40.49s | **0.53** | 0.53 | 0% |
| **Nemotron-Mini (4B)** | **8.24s** | **28.07s** | 0.26 | 0.50 | +92% |

---

## Model Selection Rationale
The following models were selected to represent different trade-offs between size, speed, and domain specialization:

1.  **Llama 3.2 (3B)**: Chosen as the representative for state-of-the-art general-purpose small models. It provides a baseline for high-quality reasoning in a compact footprint.
2.  **Nemotron-Mini (4B)**: Optimized by NVIDIA for high throughput and low latency. It was selected to test if speed comes at the cost of clinical accuracy.
3.  **Meditron (7B)**: A domain-specific model pre-trained on medical literature (PubMed, clinical guidelines). It represents the specialized approach to clinical RAG.
4.  **Gemma 2 (2B) & BioMistral (7B)**: Included in the roadmap for their high efficiency and biomedical fine-tuning (pending successful benchmark completion).

---

## Performance Analysis & Evidence

### 1. The "Quality Leader": Llama 3.2 (3B)
Llama 3.2 emerged as the most reliable model for clinical accuracy.
-   **Evidence**: It achieved the highest absolute faithfulness score (**0.68**) when verified.
-   **Positive Correction**: In Query 1 ("History of cancer"), its faithfulness jumped from **0.29 to 0.83** after PubMed verification, showing an exceptional ability to incorporate external clinical evidence into its final answer.
-   **Verdict**: Best for applications where accuracy is more critical than raw speed.

### 2. The "Speed Demon": Nemotron-Mini (4B)
Nemotron lived up to its name by being significantly faster than the other models.
-   **Evidence**: It maintained an average latency of **8.24s** in Standard RAG, nearly 50% faster than Llama 3.2.
-   **Weakness**: Its initial faithfulness was the lowest (**0.26**), meaning it relies heavily on external verification to be clinically useful.
-   **Verdict**: Best for real-time triage or low-latency interfaces, provided verification is always enabled.

### 3. The "Steady Performer": Meditron (7B)
Despite its medical specialization, Meditron showed surprising stability.
-   **Evidence**: Its faithfulness remained unchanged at **0.53** regardless of verification.
-   **Insight**: This suggests that Meditron's internal medical weights are already quite strong, but it may be less "plastic" in adapting to new retrieved context compared to Llama.
-   **Verdict**: Good for general medical queries, but less responsive to specific patient-record grounding improvements.

---

## Conclusion: Which Model is Better?

**For Clinical Decision Support, Llama 3.2 (3B) is the superior choice.**

### Why?
1.  **Highest Fact-Grounding**: It shows the best integration of PubMed evidence, resulting in the most faithful answers.
2.  **Efficiency**: At only 3B parameters, it outperforms the 7B Meditron model in verified faithfulness while maintaining comparable latency.
3.  **Balanced Performance**: While Nemotron is faster, the "hallucination risk" in Standard RAG for Nemotron is too high for clinical safety without constant verification overhead.

### Clinical Recommendation
Implement **Llama 3.2 (3B)** with **Verified RAG** for high-stakes clinical questions. Use **Nemotron-Mini (4B)** only for non-diagnostic tasks or administrative workflows where latency is the primary bottleneck.

---
*Report generated based on benchmark results from `benchmark_reports/`.*
