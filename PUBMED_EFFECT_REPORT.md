# Research Report: The PubMed Grounding Effect

**Objective**: Measure the impact of live PubMed verification on clinical hallucination mitigation vs. system latency.

**Model Used**: llama3.2:3b

## Comparative Metrics

| Metric | Standard RAG | Verified RAG (PubMed) | Delta |
| :--- | :---: | :---: | :---: |
| **Avg. Hallucination (Higher=Better)** | 1.00 | 1.00 | +0.0% |
| **Avg. Faithfulness** | 0.67 | 0.67 | +0.00 |
| **Avg. Latency** | 13.43s | 12.80s | -4.7% |

## Analysis
- **Hallucination Mitigation**: Indicates the effectiveness of peer-reviewed grounding in correcting model errors.
- **Computational Cost**: The latency delta represents the 'safety tax' incurred by adding external verification steps.
