#!/bin/bash

# Configuration
PORT=3000
PATIENT_1="129c6ac7-8d06-89de-ad63-0204a93e76c3" # Sumiko254 Medhurst46
PATIENT_2="ca15b832-01e4-41dd-6a52-97bd3e5510cb" # Corrin41 Jast432

echo "--- Testing Healthcare RAG API ---"

echo -e "\n\n=== Patient 1 (Chronic/Complex) ==="

echo -e "\nQuery 1.1: Condition History (Cancer)"
curl -s -X POST http://localhost:$PORT/query \
     -H "Content-Type: application/json" \
     -d "{
       \"question\": \"Does the patient have any history of cancer? If so, what type?\",
       \"patientId\": \"$PATIENT_1\"
     }" | jq '.'

echo -e "\nQuery 1.2: Medications (Specific)"
curl -s -X POST http://localhost:$PORT/query \
     -H "Content-Type: application/json" \
     -d "{
       \"question\": \"Has the patient ever been prescribed Cisplatin?\",
       \"patientId\": \"$PATIENT_1\"
     }" | jq '.'

echo -e "\nQuery 1.3: Active Issues"
curl -s -X POST http://localhost:$PORT/query \
     -H "Content-Type: application/json" \
     -d "{
       \"question\": \"What are the patient's currently active medical conditions?\",
       \"patientId\": \"$PATIENT_1\"
     }" | jq '.'


echo -e "\n\n=== Patient 2 (Acute/Maternal) ==="

echo -e "\nQuery 2.1: Pregnancy History"
curl -s -X POST http://localhost:$PORT/query \
     -H "Content-Type: application/json" \
     -d "{
       \"question\": \"Is there any record of a normal pregnancy for this patient?\",
       \"patientId\": \"$PATIENT_2\"
     }" | jq '.'

echo -e "\nQuery 2.2: COVID-19"
curl -s -X POST http://localhost:$PORT/query \
     -H "Content-Type: application/json" \
     -d "{
       \"question\": \"Has the patient had any suspected respiratory infections like COVID-19?\",
       \"patientId\": \"$PATIENT_2\"
     }" | jq '.'


echo -e "\n\n=== Negative Controls / Robustness (Not Patient Specific) ==="

echo -e "\nQuery 4.1: General Medical Question (No Patient Context)"
curl -s -X POST http://localhost:$PORT/query \
     -H "Content-Type: application/json" \
     -d "{
       \"question\": \"What are the primary long-term complications of poorly managed Type 2 Diabetes?\"
     }" | jq '.'

echo -e "\nQuery 4.2: Invalid Patient ID / No Records"
curl -s -X POST http://localhost:$PORT/query \
     -H "Content-Type: application/json" \
     -d "{
       \"question\": \"Has this patient had any history of heart surgery?\",
       \"patientId\": \"INVALID-ID-000000\"
     }" | jq '.'
