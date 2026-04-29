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
        "patientId": "ca15b832-01e4-41dd-6a52-97bd3e5510cb",
        "input": "Is there any record of a normal pregnancy for this patient?",
        "expected_output": "Yes, there is a record of a normal pregnancy for this patient between 2017-12-27 and 2018-08-01.",
        "retrieval_context": [
            "Condition: Normal pregnancy. Onset: 2017-12-27. Abatement: 2018-08-01."
        ]
    },

    {
        "patientId": "129c6ac7-8d06-89de-ad63-0204a93e76c3",
        "input": "Is the patient currently being treated for cancer and are they experiencing stress?",
        "expected_output": "The patient is currently being treated for Non-small cell lung cancer, which is active. However, their history of stress is resolved.",
        "retrieval_context": [
            "Condition: Non-small cell lung cancer (disorder). Status: active.",
            "Condition: Stress (finding). Status: resolved."
        ]
    },
    {
        "patientId": "ca15b832-01e4-41dd-6a52-97bd3e5510cb",
        "input": "Did the patient have suspected COVID-19 while they were pregnant?",
        "expected_output": "No, the patient was pregnant from December 2017 to August 2018, and had suspected COVID-19 later in January 2021.",
        "retrieval_context": [
            "Condition: Suspected COVID-19. Onset: 2021-01-23. Abatement: 2021-01-23.",
            "Condition: Normal pregnancy. Onset: 2017-12-27. Abatement: 2018-08-01."
        ]
    },
    {
        "patientId": "129c6ac7-8d06-89de-ad63-0204a93e76c3",
        "input": "Does the patient have any active diagnosis of Type 2 Diabetes or HIV?",
        "expected_output": "Yes, the patient was diagnosed with Type 2 Diabetes and HIV in 2020 and is currently taking Metformin.",
        "retrieval_context": [
            "Condition: Non-small cell lung cancer (disorder). Status: active. Onset: 1984-10-31T19:35:22-05:00."
        ]
    }
]
