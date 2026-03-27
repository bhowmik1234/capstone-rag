# Capstone Research Proposal: Advancing Clinical RAG Systems

Based on the developed healthcare Retrieval-Augmented Generation (RAG) architecture, this document outlines two primary research directions for the capstone project. These directions leverage the system's unique local execution, FHIR integration, and DeepEval automated verification.

---

## Research Direction 1: Comparative Analysis of General vs. Medical-Specific LLMs in a Clinical RAG Pipeline

**The Problem:**
General-purpose Large Language Models (LLMs) like Llama 3 often struggle with the nuances of clinical terminology and temporal medical reasoning when analyzing patient records.

**The Hypothesis:**
Domain-specific medical LLMs (e.g., Med42, BioMistral, Meditron) will exhibit significantly lower hallucination rates and higher factual faithfulness compared to similarly sized general-purpose LLMs when operating within a clinical RAG pipeline.

**Methodology:**
1.  **Dataset**: Utilize the custom "Golden Dataset" of 5 diverse clinical queries covering oncology, maternal health, and active diagnosis status based on FHIR data.
2.  **Execution**: Run the automated benchmarking script (`run_full_benchmark.py`) to systematically test multiple models under identical retrieval conditions.
    *   *Control Group*: General Models (Llama 3.2 3B, Llama 3.2 1B).
    *   *Test Group*: Medical Models (Med42-8B, Meditron-7B, BioMistral-7B).
3.  **Metrics**: Use DeepEval to calculate:
    *   **Faithfulness**: To ensure the model does not invent FHIR data.
    *   **Hallucination Rate**: To measure logical contradictions.
    *   **Latency**: To assess the computational trade-off of using specialized models.

**Expected Outcome:**
A published matrix proving exactly how much "safer" medical-specific models are for analyzing private patient records locally, quantifying the trade-off in latency vs. clinical accuracy.

---

## Research Direction 2: The "PubMed Grounding" Effect on Hallucination Mitigation

**The Problem:**
Even with perfect retrieval from local FHIR databases, LLMs can hallucinate medical facts or fail to synthesize patient data with current medical standards when generating a response.

**The Hypothesis:**
Introducing an active, live "Verification Chain" that queries a public medical literature database (PubMed) prior to final answer generation will drastically reduce clinical hallucinations, albeit with a measurable penalty to system latency.

**Methodology:**
1.  **A/B Testing Framework**:
    *   *System A (Standard RAG)*: Vector Retrieval -> LLM Generation -> Output.
    *   *System B (Verified RAG)*: Vector Retrieval -> LLM Generation -> PubMed Keyword Extraction -> PubMed Search -> LLM Verification -> Final Output.
2.  **Execution**: Modify the current architecture to bypass the `verifyAndRefine` step for System A. Run the complete evaluation suite on both System A and System B using the top-performing model from Research Direction 1.
3.  **Metrics Analysis**:
    *   Measure the exact percentage decrease in the "Hallucination" score between System A and System B.
    *   Calculate the exact increase in average latency (seconds).

**Expected Outcome:**
A quantitative analysis arguing whether the high computational and temporal cost of live medical literature verification is justifiable in a production healthcare environment compared to the resulting increase in clinical safety.
