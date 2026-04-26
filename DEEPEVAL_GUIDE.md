# DeepEval Framework in Healthcare RAG

DeepEval is an open-source evaluation framework for LLMs. In this project, it acts as an **Automated Clinical Judge**, scoring the performance, safety, and accuracy of our Healthcare RAG system against a curated "Golden Dataset."

---

## DeepEval Workflow

The evaluation process operates by feeding a test query into our live API, capturing the response, and then using a separate, independent LLM evaluator to score that response against our ground truth.

```mermaid
sequence_diagram
    participant Test as evaluate_rag.py
    participant API as Node.js Backend
    participant DB as VectorDB (LanceDB)
    participant Judge as DeepEval Evaluator (Llama 3.2)
    participant Data as Golden Dataset
    
    Test->>API: POST /query (Patient ID, Question)
    API->>DB: Retrieve FHIR Context
    DB-->>API: Clinical Records
    API-->>Test: Actual Answer + Retrieved Context
    
    Test->>Data: Fetch Expected Output
    Data-->>Test: Golden Answer
    
    Test->>Judge: Send LLMTestCase (Input, Actual, Expected, Context)
    Judge-->>Judge: Calculate Faithfulness
    Judge-->>Judge: Calculate Answer Relevancy
    Judge-->>Judge: Calculate Hallucination
    Judge-->>Judge: Calculate Contextual Relevancy
    
    Judge-->>Test: Final Scores
    Test->>Report: Generate Benchmark Printout
```

---

## In-Depth Metric Explanations

In a healthcare setting, traditional NLP metrics (like BLEU or ROUGE) are insufficient because they only measure word overlap. DeepEval uses **LLM-Evaluated Metrics**, which can assess factual consistency, tone, and logical reasoning.

We use the following four core metrics:

### 1. Faithfulness (Groundedness)
*   **What it measures:** Fact-checking. It verifies if the `actual_output` (the final answer given to the doctor) contains facts that are *strictly supported* by the `retrieval_context` (the patient's FHIR records).
*   **Why it matters in Healthcare:** This is the most critical metric. If the system tells a doctor the patient had a heart attack, but the FHIR records only mention hypertension, the Faithfulness score plummets. It prevents the model from bringing in outside knowledge.
*   **How it works:** The evaluator extracts all claims made in the answer, checks them one-by-one against the context, and calculates a ratio of truthful claims to total claims.

### 2. Hallucination Risk
*   **What it measures:** The tendency of the model to invent information.
*   **Why it matters in Healthcare:** Similar to Faithfulness, but focuses specifically on penalizing the model for adding details that contradict or are entirely absent from the provided context or common medical sense.
*   **How it works:** The evaluator looks for logical inconsistencies or fabricated facts in the generation step.

### 3. Answer Relevancy
*   **What it measures:** Actionability. Does the `actual_output` concisely answer the original `input` question without rambling?
*   **Why it matters in Healthcare:** Doctors are time-poor. If they ask about "active side effects of Cisplatin", they don't want a 3-paragraph summary of the patient's entire oncology history. High Answer Relevancy means low fluff.
*   **How it works:** The evaluator creates hypothetical questions based on the generated answer. If those hypothetical questions match the *original* user question, the relevancy score is high.

### 4. Contextual Relevancy (Retrieval Quality)
*   **What it measures:** The accuracy of our Vector Search (LanceDB). Does the `retrieval_context` actually contain the information needed to answer the question?
*   **Why it matters in Healthcare:** If a doctor asks about an allergy, but the Vector DB retrieves 5 "Observation" (Vitals) records and 0 "AllergyIntolerance" records, the generator is doomed from the start. 
*   **How it works:** The evaluator reads the context and determines if the text snippets are highly relevant to the user's prompt. It helps us debug if our vector embeddings (`nomic-embed-text`) are failing.

---

## Configuration in our Pipeline

We configure DeepEval to use **local LLMs** instead of OpenAI. This ensures our evaluation process remains completely private, allowing us to evaluate PHI (Protected Health Information) without sending data to external servers.

```python
# evaluate_rag.py snippet
custom_model = OllamaModel(model="llama3.2:1b")

test_case = LLMTestCase(
    input=entry['input'],
    actual_output=actual_output,
    expected_output=entry['expected_output'],
    retrieval_context=entry['retrieval_context'],
    context=entry['retrieval_context']
)

# Strict evaluation (0.7 threshold = 70% confidence required to "pass")
FaithfulnessMetric(threshold=0.7, model=custom_model).measure(test_case)
```
