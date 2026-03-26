
# Comparative Research Report: Large Language Models for Edge Computing (Mac M2)

## 1. Abstract
This report evaluates the performance and technical specifications of several state-of-the-art Large Language Models (LLMs) running locally via Ollama on a Mac M2 with 8GB RAM. The goal is to identify the most efficient model for clinical RAG (Retrieval-Augmented Generation) applications under significant memory constraints.



## 2. Technical Specifications

| Feature | Llama 3.1 (8B) | Llama 3.2 (3B) | Llama 3.2 (1B) | Phi-3 Mini (3.8B) |
| :--- | :--- | :--- | :--- | :--- |
| **Architecture** | Dense Transformer | Dense Transformer | Dense Transformer | Dense Transformer |
| **Parameters** | 8.0 Billion | 3.2 Billion | 1.2 Billion | 3.8 Billion |
| **Quantization** | Q4_K_M (4-bit) | Q4_K_M (4-bit) | Q8_0 (8-bit) | Q4 (Standard) |
| **Context Window** | 131,072 tokens | 131,072 tokens | 131,072 tokens | 128,000 tokens |
| **Embedding Dim** | 4,096 | 3,072 | 2,048 | 3,072 |
| **On-Disk Size** | ~4.7 GB | ~2.0 GB | ~1.3 GB | ~2.3 GB |
| **Hungry RAM** | High (>5GB) | Moderate (~2.5GB) | Low (~1.5GB) | Moderate (~2.8GB) |



## 3. Performance Analysis (Mac M2 / 8GB RAM)

### 3.1 Latency Benchmarks
Average response time for healthcare clinical queries (seconds):

*   **Llama 3.1 (8B):** **33.78s** (Significant bottleneck; causes system swap/pressure).
*   **Llama 3.2 (3B):** **11.76s** (Optimal balance; maintains context sensitivity while remaining snappy).
*   **Llama 3.2 (1B):** **4.99s** (Ultra-low latency; useful for high-throughput simple classification).
*   **Phi-3 Mini:** (N/A locally due to download error, but theoretical performance mirrors Llama 3.2 3B).




### 3.2 Observational Quality
*   **Llama 3.1:** Highest reasoning capability but effectively unusable for interactive apps on 8GB RAM.
*   **Llama 3.2 (3B):** Very high fidelity in extracting clinical facts from FHIR context.
*   **Llama 3.2 (1B):** Occasionally hallucinates minor details in long clinical contexts but excellent for "Yes/No" or "List" extraction.


