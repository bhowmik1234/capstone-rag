#!/bin/bash

# Configuration
PORT=3000
PATIENT_ID="129c6ac7-8d06-89de-ad63-0204a93e76c3"

echo "--- Testing Healthcare RAG API ---"

# echo -e "\n\nQuery 1: Conditions/Diagnosis"
# curl -s -X POST http://localhost:$PORT/query \
#      -H "Content-Type: application/json" \
#      -d "{
#        \"question\": \"Does the patient have any history of respiratory conditions?\",
#        \"patientId\": \"$PATIENT_ID\"
#      }" | jq '.'

echo -e "\n\nQuery 2: Medications"
curl -s -X POST http://localhost:$PORT/query \
     -H "Content-Type: application/json" \
     -d "{
       \"question\": \"What medications is the patient currently taking?\",
       \"patientId\": \"$PATIENT_ID\"
     }" | jq '.'
