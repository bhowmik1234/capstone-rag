import os
from typing import List, Dict

# Golden Dataset for Healthcare RAG Evaluation
# Format: List of Dict with keys: 'input', 'actual_output', 'expected_output', 'retrieval_context'

GOLDEN_DATASET = [
    {
        "patientId": "129c6ac7-8d06-89de-ad63-0204a93e76c3",
        "input": "Does the patient have any history of cancer? If so, what type?",
        "expected_output": "Yes, the patient has a history of Non-small cell lung cancer (disorder), which was recorded as an active condition starting in 1984.",
        "retrieval_context": [
            "Condition: Non-small cell lung cancer (disorder). Status: active. Onset: 1984-10-31T19:35:22-05:00."
        ]
    },
    {
        "patientId": "129c6ac7-8d06-89de-ad63-0204a93e76c3",
        "input": "Has the patient ever been prescribed Cisplatin?",
        "expected_output": "Yes, the patient was prescribed Cisplatin 50 MG Injection on 1987-03-08 as part of their treatment for non-small cell carcinoma of lung.",
        "retrieval_context": [
            "MedicationRequest: Cisplatin 50 MG Injection. Status: stopped. AuthoredOn: 1987-03-08. Reason: Non-small cell carcinoma of lung."
        ]
    },
    {
        "patientId": "129c6ac7-8d06-89de-ad63-0204a93e76c3",
        "input": "What are the patient's currently active medical conditions?",
        "expected_output": "The patient's currently active medical condition is Non-small cell lung cancer (disorder). The history of Stress (finding) is resolved.",
        "retrieval_context": [
            "Condition: Non-small cell lung cancer (disorder). Status: active.",
            "Condition: Stress (finding). Status: resolved."
        ]
    },
    {
        "patientId": "ca15b832-01e4-41dd-6a52-97bd3e5510cb",
        "input": "Is there any record of a normal pregnancy for this patient?",
        "expected_output": "Yes, there is a record of a normal pregnancy for this patient between 2017-12-27 and 2018-08-01.",
        "retrieval_context": [
            "Condition: Normal pregnancy. Onset: 2017-12-27. Abatement: 2018-08-01."
        ]
    },
    {
        "patientId": "ca15b832-01e4-41dd-6a52-97bd3e5510cb",
        "input": "Has the patient had any suspected respiratory infections like COVID-19?",
        "expected_output": "Yes, there is a record of 'Suspected COVID-19' for this patient on 2021-01-23.",
        "retrieval_context": [
            "Condition: Suspected COVID-19. Onset: 2021-01-23. Abatement: 2021-01-23."
        ]
    }
]
