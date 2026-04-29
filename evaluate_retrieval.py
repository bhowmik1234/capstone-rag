import requests
import time
from golden_dataset import GOLDEN_DATASET

API_URL = "http://localhost:3000/query"

def calculate_metrics(retrieved_sources, expected_chunks, k=3):
    top_k_sources = retrieved_sources[:k]
    
    # Calculate hits
    hits = 0
    first_hit_rank = 0
    
    for expected in expected_chunks:
        # Check if this expected chunk is found in the top-k retrieved sources
        found = False
        for rank, source in enumerate(top_k_sources):
            # Simple substring matching, ignoring case and some spaces
            if expected.lower() in source['summary'].lower() or source['summary'].lower() in expected.lower() or expected[:20].lower() in source['summary'].lower():
                found = True
                if first_hit_rank == 0 or rank + 1 < first_hit_rank:
                    first_hit_rank = rank + 1
                break
        if found:
            hits += 1

    precision = hits / k
    recall = hits / len(expected_chunks) if len(expected_chunks) > 0 else 0
    mrr = 1.0 / first_hit_rank if first_hit_rank > 0 else 0.0

    return precision, recall, mrr

def evaluate_strategy(strategy):
    total_precision = 0
    total_recall = 0
    total_mrr = 0
    
    print(f"\nEvaluating strategy: {strategy.upper()}...")
    
    for i, entry in enumerate(GOLDEN_DATASET):
        payload = {
            "question": entry["input"],
            "patientId": entry.get("patientId"),
            "skipPubMed": True,
            "retrievalStrategy": strategy
        }
        
        try:
            resp = requests.post(API_URL, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                sources = data.get("sources", [])
                expected = entry.get("retrieval_context", [])
                
                p, r, m = calculate_metrics(sources, expected, k=3)
                total_precision += p
                total_recall += r
                total_mrr += m
            else:
                print(f"Error for query {i}: {resp.text}")
        except Exception as e:
            print(f"Request failed for query {i}: {e}")
            
    n = len(GOLDEN_DATASET)
    return {
        "Precision@3": total_precision / n,
        "Recall@3": total_recall / n,
        "MRR": total_mrr / n
    }

def main():
    strategies = ["bm25", "embedding", "hybrid"]
    results = {}
    
    for s in strategies:
        results[s] = evaluate_strategy(s)
        time.sleep(1) # Small pause
        
    print("\n\n🔥 Final Evaluation Results 🔥")
    
    print("\\begin{table}[h]")
    print("\\centering")
    print("\\caption{Retrieval Performance}")
    print("\\begin{tabular}{lccc}")
    print("\\hline")
    print("Method & Precision@3 & Recall@3 & MRR \\\\")
    print("\\hline")
    
    # Format the rows
    methods_map = {
        "bm25": "BM25",
        "embedding": "Embedding",
        "hybrid": "Hybrid (Proposed)"
    }
    
    for s in strategies:
        p = results[s]['Precision@3']
        r = results[s]['Recall@3']
        m = results[s]['MRR']
        
        name = methods_map[s]
        
        if s == "hybrid":
            print(f"{name} & \\textbf{{{p:.2f}}} & \\textbf{{{r:.2f}}} & \\textbf{{{m:.2f}}} \\\\")
        else:
            print(f"{name} & {p:.2f} & {r:.2f} & {m:.2f} \\\\")
            
    print("\\hline")
    print("\\end{tabular}")
    print("\\end{table}")

if __name__ == "__main__":
    main()
