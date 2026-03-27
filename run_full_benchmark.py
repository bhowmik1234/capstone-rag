import subprocess
import os
import time
import json
import re

# Models to benchmark
MODELS = [
    "llama3.2:3b",
    "llama3.1:8b", 
    "llama3.2:1b", 
    "meditron:7b", 
    "biomistral:7b", 
    "med42", 
    "nemotron", 
    "mistral-nemo"
]
REPORT_FILE = "BENCHMARK_REPORT.md"
EVAL_SCRIPT = "evaluate_rag.py"
SERVER_CMD = ["npm", "run", "dev"]
HEALTH_CHECK_URL = "http://localhost:3000/query"

def ensure_model_pulled(model):
    print(f"Checking if {model} is available locally...")
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    if model not in result.stdout:
        print(f"Model {model} not found. Pulling now (this may take a while)...")
        subprocess.run(["ollama", "pull", model])
    else:
        print(f"Model {model} is ready.")

def run_benchmark():
    all_results = {}

    for model in MODELS:
        print(f"\n>>> Benchmarking Model: {model} <<<")
        ensure_model_pulled(model)
        
        # 1. Start Server with model environment variable
        env = os.environ.copy()
        env["CHAT_MODEL"] = model
        # Disable tsx watch to avoid accidental restarts during eval
        env["TSX_WATCH"] = "false" 
        
        process = subprocess.Popen(
            SERVER_CMD,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=os.getcwd()
        )

        # 2. Wait for Server to be ready
        print("Starting server and waiting for readiness...")
        is_ready = False
        start_wait = time.time()
        while time.time() - start_wait < 60:
            line = process.stdout.readline()
            if "Healthcare RAG Backend running" in line:
                print("Server is ready!")
                is_ready = True
                break
            if process.poll() is not None:
                print("Server failed to start.")
                break
        
        if not is_ready:
            print(f"Skipping {model} due to server startup failure.")
            process.terminate()
            continue

        # 3. Run Evaluation Script
        print(f"Running evaluation suite for {model}...")
        try:
            eval_proc = subprocess.run(
                ["python3", EVAL_SCRIPT],
                env=env,
                capture_output=True,
                text=True,
                timeout=1200 # 20 mins max for all queries
            )
            eval_output = eval_proc.stdout
            print(eval_output)
            
            # 4. Parse Metrics from Output
            metrics = parse_metrics(eval_output)
            all_results[model] = metrics
            
        except subprocess.TimeoutExpired:
            print(f"Evaluation for {model} timed out.")
        except Exception as e:
            print(f"Error during evaluation: {e}")
        finally:
            # 5. Stop Server
            print(f"Stopping server for {model}...")
            process.terminate()
            process.wait()

    # 6. Generate Report
    generate_report(all_results)

def parse_metrics(output):
    metrics = {}
    patterns = {
        "latency": r"Average Latency: ([\d.]+)s",
        "faithfulness": r"Average Faithfulness: ([\d.]+)",
        "relevancy": r"Average Answerrelevancy: ([\d.]+)",
        "hallucination": r"Average Hallucination: ([\d.]+)",
        "contextual_rel": r"Average Contextualrelevancy: ([\d.]+)",
        "success_rate": r"Overall Success Rate: ([\d.]+)%"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            metrics[key] = match.group(1)
        else:
            metrics[key] = "N/A"
    return metrics

def generate_report(results):
    with open(REPORT_FILE, "w") as f:
        f.write("# Multi-Model RAG Benchmark Report\n\n")
        f.write("Generated automatically to compare clinical RAG performance across different local LLMs.\n\n")
        
        # Table Header
        f.write("| Metric | " + " | ".join(MODELS) + " |\n")
        f.write("| :--- | " + " | ".join([":---:"] * len(MODELS)) + " |\n")
        
        keys = [
            ("Avg. Latency", "latency", "s"),
            ("Avg. Faithfulness", "faithfulness", ""),
            ("Avg. Hallucination", "hallucination", ""),
            ("Avg. Contextual Rel.", "contextual_rel", ""),
            ("Overall Success Rate", "success_rate", "%")
        ]
        
        for label, key, unit in keys:
            row = f"| {label} | "
            row += " | ".join([f"{results.get(m, {}).get(key, 'N/A')}{unit}" for m in MODELS])
            row += " |\n"
            f.write(row)
        
        f.write("\n## Observations\n")
        f.write("- **Faithfulness**: Higher is better (less hallucination).\n")
        f.write("- **Hallucination**: High score means low hallucination rate (factual grounding).\n")
        f.write("- **Contextual Relevancy**: Measures how relevant the retrieved context is to the query.\n")

    print(f"\n--- Benchmark Complete! Report saved to {REPORT_FILE} ---")

if __name__ == "__main__":
    run_benchmark()
