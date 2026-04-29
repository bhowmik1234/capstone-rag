import subprocess
import os
import time
import json
import requests
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric, HallucinationMetric, ContextualRelevancyMetric, ContextualPrecisionMetric, ContextualRecallMetric
from deepeval.test_case import LLMTestCase
from deepeval.models.llms.ollama_model import OllamaModel
from golden_dataset import GOLDEN_DATASET
from dotenv import load_dotenv

load_dotenv()

# Disable DeepEval's strict per-attempt timeout (default is 88.5s)
os.environ["DEEPEVAL_PER_ATTEMPT_TIMEOUT_SECONDS_OVERRIDE"] = "600"

# Select the model you want to run (Edit this for individual runs)
TARGET_MODEL = "meditron:7b" 
MODELS = [
    "llama3.2:3b",
    "nemotron-mini:4b",
    "meditron:7b",
    "biomistral:7b"
]

API_URL = "http://localhost:3000/query"
REPORT_DIR = "./benchmark_reports"
SERVER_CMD = ["/usr/local/bin/npm", "run", "dev"]
OLLAMA_PATH = "/usr/local/bin/ollama"

os.makedirs(REPORT_DIR, exist_ok=True)

def ensure_model_pulled(model):
    print(f"\n[SYSTEM] Ensuring model is ready: {model}...")
    subprocess.run([OLLAMA_PATH, "pull", model])

def calculate_lexical_change(text1, text2):
    """Measures how much the refined answer deviated from the original."""
    import difflib
    return difflib.SequenceMatcher(None, text1, text2).ratio()

def run_individual_bench(model_name):
    print(f"\n{'='*60}")
    print(f"SCIENTIFIC BENCHMARK: {model_name}")
    print(f"{'='*60}")
    
    ensure_model_pulled(model_name)
    
    # Start Server (Shared for all 5 queries of this model)
    env = os.environ.copy()
    env["CHAT_MODEL"] = model_name
    env["TSX_WATCH"] = "false"
    env["PATH"] = "/usr/local/bin:" + env.get("PATH", "")
    
    server_proc = subprocess.Popen(
        SERVER_CMD,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=os.getcwd()
    )

    # Wait for readiness
    is_ready = False
    start_wait = time.time()
    while time.time() - start_wait < 90:
        line = server_proc.stdout.readline()
        if "Healthcare RAG Backend running" in line:
            print(f"Server ready for {model_name}")
            is_ready = True
            break
    
    if not is_ready:
        print(f"Failed to start server for {model_name}")
        server_proc.terminate()
        return

    evaluator_model = OllamaModel(model=model_name)
    query_reports = []

    try:
        for i, entry in enumerate(GOLDEN_DATASET):
            print(f"\n[QUERY {i+1}] Processing: {entry['input'][:60]}...")
            
            # --- STEP 1: STANDARD RAG ---
            print(f"  -> Step 1/4: Executing Standard RAG...")
            start_std = time.time()
            resp_std = requests.post(API_URL, json={
                "question": entry['input'], "patientId": entry['patientId'], "skipPubMed": True
            }, timeout=300).json()
            lat_std = time.time() - start_std
            ans_std = resp_std.get("answer", "")
            
            tc_std = LLMTestCase(input=entry['input'], actual_output=ans_std, expected_output=entry['expected_output'], retrieval_context=entry['retrieval_context'], context=entry['retrieval_context'])
            mf_std = FaithfulnessMetric(threshold=0.7, model=evaluator_model)
            mf_std.measure(tc_std)
            mh_std = HallucinationMetric(threshold=0.7, model=evaluator_model)
            mh_std.measure(tc_std)
            mar_std = AnswerRelevancyMetric(threshold=0.7, model=evaluator_model)
            mar_std.measure(tc_std)
            mcr_std = ContextualRelevancyMetric(threshold=0.7, model=evaluator_model)
            mcr_std.measure(tc_std)
            mcp_std = ContextualPrecisionMetric(threshold=0.7, model=evaluator_model)
            mcp_std.measure(tc_std)
            mcrecall_std = ContextualRecallMetric(threshold=0.7, model=evaluator_model)
            mcrecall_std.measure(tc_std)
            
            print(f"     Standard Results: Latency: {lat_std:.2f}s | Faith: {mf_std.score:.2f} | Hallu: {mh_std.score:.2f} | AnsRel: {mar_std.score:.2f} | CtxRel: {mcr_std.score:.2f} | CtxPrec: {mcp_std.score:.2f} | CtxRecall: {mcrecall_std.score:.2f}")

            # --- STEP 2: VERIFIED RAG (PUBMED) ---
            print(f"  -> Step 2/4: Executing Verified RAG...")
            start_ver = time.time()
            resp_ver = requests.post(API_URL, json={
                "question": entry['input'], "patientId": entry['patientId'], "skipPubMed": False
            }, timeout=300).json()
            lat_ver = time.time() - start_ver
            ans_ver = resp_ver.get("answer", "")
            ver_text = resp_ver.get("verification", "")
            sources = len(resp_ver.get("pubmedArticles", []))
            
            tc_ver = LLMTestCase(input=entry['input'], actual_output=ans_ver, expected_output=entry['expected_output'], retrieval_context=entry['retrieval_context'], context=entry['retrieval_context'])
            mf_ver = FaithfulnessMetric(threshold=0.7, model=evaluator_model)
            mf_ver.measure(tc_ver)
            mh_ver = HallucinationMetric(threshold=0.7, model=evaluator_model)
            mh_ver.measure(tc_ver)
            mar_ver = AnswerRelevancyMetric(threshold=0.7, model=evaluator_model)
            mar_ver.measure(tc_ver)
            mcr_ver = ContextualRelevancyMetric(threshold=0.7, model=evaluator_model)
            mcr_ver.measure(tc_ver)
            mcp_ver = ContextualPrecisionMetric(threshold=0.7, model=evaluator_model)
            mcp_ver.measure(tc_ver)
            mcrecall_ver = ContextualRecallMetric(threshold=0.7, model=evaluator_model)
            mcrecall_ver.measure(tc_ver)
            
            print(f"     Verified Results: Latency: {lat_ver:.2f}s | Faith: {mf_ver.score:.2f} | Hallu: {mh_ver.score:.2f} | AnsRel: {mar_ver.score:.2f} | CtxRel: {mcr_ver.score:.2f} | CtxPrec: {mcp_ver.score:.2f} | CtxRecall: {mcrecall_ver.score:.2f} | Sources: {sources}")

            # --- STEP 3: ANALYZE DEVIATION ---
            lex_similarity = calculate_lexical_change(ans_std, ans_ver)
            change_impact = "Significant" if lex_similarity < 0.7 else "Moderate" if lex_similarity < 0.9 else "Minor"
            
            # Formulate Per-Query Report
            query_reports.append({
                "id": i+1,
                "input": entry['input'],
                "latency_std": lat_std, "latency_ver": lat_ver,
                "faith_std": {"score": mf_std.score, "success": mf_std.is_successful, "reason": getattr(mf_std, 'reason', '')},
                "hallu_std": {"score": mh_std.score, "success": mh_std.is_successful, "reason": getattr(mh_std, 'reason', '')},
                "ans_rel_std": {"score": mar_std.score, "success": mar_std.is_successful, "reason": getattr(mar_std, 'reason', '')},
                "ctx_rel_std": {"score": mcr_std.score, "success": mcr_std.is_successful, "reason": getattr(mcr_std, 'reason', '')},
                "ctx_prec_std": {"score": mcp_std.score, "success": mcp_std.is_successful, "reason": getattr(mcp_std, 'reason', '')},
                "ctx_recall_std": {"score": mcrecall_std.score, "success": mcrecall_std.is_successful, "reason": getattr(mcrecall_std, 'reason', '')},
                
                "faith_ver": {"score": mf_ver.score, "success": mf_ver.is_successful, "reason": getattr(mf_ver, 'reason', '')},
                "hallu_ver": {"score": mh_ver.score, "success": mh_ver.is_successful, "reason": getattr(mh_ver, 'reason', '')},
                "ans_rel_ver": {"score": mar_ver.score, "success": mar_ver.is_successful, "reason": getattr(mar_ver, 'reason', '')},
                "ctx_rel_ver": {"score": mcr_ver.score, "success": mcr_ver.is_successful, "reason": getattr(mcr_ver, 'reason', '')},
                "ctx_prec_ver": {"score": mcp_ver.score, "success": mcp_ver.is_successful, "reason": getattr(mcp_ver, 'reason', '')},
                "ctx_recall_ver": {"score": mcrecall_ver.score, "success": mcrecall_ver.is_successful, "reason": getattr(mcrecall_ver, 'reason', '')},
                "sources": sources,
                "change_impact": change_impact,
                "lex_similarity": lex_similarity,
                "ans_std": ans_std,
                "ans_ver": ans_ver,
                "ver_text": ver_text
            })

    finally:
        server_proc.terminate()
    
    generate_model_md_report(model_name, query_reports)
    return query_reports

def generate_model_md_report(model_name, reports):
    timestamp = int(time.time())
    report_path = f"{REPORT_DIR}/RESEARCH_REPORT_{model_name.replace(':', '_')}_{timestamp}.md"
    
    with open(report_path, "w") as f:
        f.write(f"# Scientific Research Report: {model_name}\n\n")
        f.write(f"**Objective**: Analyze model deviation and grounding quality shift through clinical RAG verification.\n\n")
        
        # Add Glossary
        f.write("## 📚 Metric Glossary\n")
        f.write("- **Faithfulness**: Measures if the generated answer is factually accurate based strictly on the retrieved context (no fabrication).\n")
        f.write("- **Hallucination**: Evaluates if the model directly contradicts the source context.\n")
        f.write("- **Answer Relevancy**: Assesses if the generated response directly and concisely answers the original question without going off-topic.\n")
        f.write("- **Contextual Relevancy**: Evaluates the quality of retrieval by checking the proportion of relevant vs irrelevant retrieved chunks.\n")
        f.write("- **Contextual Precision**: Measures if the most relevant nodes are ranked highly in the retrieval results.\n")
        f.write("- **Contextual Recall**: Measures if the retriever fetched *all* necessary facts to answer the question.\n\n")
        
        f.write("## 📊 Executive Metrics Summary\n")
        avg_lat_std = sum(r['latency_std'] for r in reports) / len(reports)
        avg_lat_ver = sum(r['latency_ver'] for r in reports) / len(reports)
        
        def get_stats(key):
            scores = [r[key]['score'] for r in reports]
            passes = [1 if r[key]['success'] else 0 for r in reports]
            return sum(scores)/len(scores), (sum(passes)/len(passes))*100
            
        f_std_s, f_std_p = get_stats('faith_std')
        f_ver_s, f_ver_p = get_stats('faith_ver')
        h_std_s, h_std_p = get_stats('hallu_std')
        h_ver_s, h_ver_p = get_stats('hallu_ver')
        ar_std_s, ar_std_p = get_stats('ans_rel_std')
        ar_ver_s, ar_ver_p = get_stats('ans_rel_ver')
        cr_std_s, cr_std_p = get_stats('ctx_rel_std')
        cr_ver_s, cr_ver_p = get_stats('ctx_rel_ver')
        cp_std_s, cp_std_p = get_stats('ctx_prec_std')
        cp_ver_s, cp_ver_p = get_stats('ctx_prec_ver')
        cre_std_s, cre_std_p = get_stats('ctx_recall_std')
        cre_ver_s, cre_ver_p = get_stats('ctx_recall_ver')
        
        f.write(f"**Average Latency**: {avg_lat_std:.2f}s (Std) vs {avg_lat_ver:.2f}s (Ver) | Shift: {((avg_lat_ver-avg_lat_std)/max(0.1, avg_lat_std))*100:+.1f}%\n")
        f.write(f"**Total PubMed Citations**: {sum(r['sources'] for r in reports)}\n\n")
        
        f.write("### Generation Quality\n")
        f.write(f"| Metric | Standard RAG | Verified RAG | Score Shift |\n")
        f.write(f"| :--- | :--- | :--- | :---: |\n")
        f.write(f"| **Faithfulness** | {f_std_s:.2f} ({f_std_p:.0f}% Pass) | {f_ver_s:.2f} ({f_ver_p:.0f}% Pass) | {f_ver_s-f_std_s:+.2f} |\n")
        f.write(f"| **Hallucination** | {h_std_s:.2f} ({h_std_p:.0f}% Pass) | {h_ver_s:.2f} ({h_ver_p:.0f}% Pass) | {h_ver_s-h_std_s:+.2f} |\n")
        f.write(f"| **Answer Relevancy** | {ar_std_s:.2f} ({ar_std_p:.0f}% Pass) | {ar_ver_s:.2f} ({ar_ver_p:.0f}% Pass) | {ar_ver_s-ar_std_s:+.2f} |\n\n")

        f.write("### Retrieval Quality\n")
        f.write(f"| Metric | Standard RAG | Verified RAG | Score Shift |\n")
        f.write(f"| :--- | :--- | :--- | :---: |\n")
        f.write(f"| **Context Relevancy** | {cr_std_s:.2f} ({cr_std_p:.0f}% Pass) | {cr_ver_s:.2f} ({cr_ver_p:.0f}% Pass) | {cr_ver_s-cr_std_s:+.2f} |\n")
        f.write(f"| **Context Precision** | {cp_std_s:.2f} ({cp_std_p:.0f}% Pass) | {cp_ver_s:.2f} ({cp_ver_p:.0f}% Pass) | {cp_ver_s-cp_std_s:+.2f} |\n")
        f.write(f"| **Context Recall** | {cre_std_s:.2f} ({cre_std_p:.0f}% Pass) | {cre_ver_s:.2f} ({cre_ver_p:.0f}% Pass) | {cre_ver_s-cre_std_s:+.2f} |\n\n")

        f.write("## 🔍 Deep Query Analysis\n\n")
        for r in reports:
            f.write(f"### Query {r['id']}: {r['input']}\n")
            f.write(f"**Verification Impact**: {r['change_impact']} (Lexical Similarity: {r['lex_similarity']:.2f})\n\n")
            
            f.write(f"#### Latency & Sources\n")
            f.write(f"- Standard: {r['latency_std']:.2f}s\n")
            f.write(f"- Verified: {r['latency_ver']:.2f}s (Includes {r['sources']} PubMed citations)\n\n")
            
            f.write("#### Metric Reasoning\n")
            f.write("| Metric | Standard RAG | Verified RAG |\n")
            f.write("| :--- | :--- | :--- |\n")
            f.write(f"| **Faithfulness** | {r['faith_std']['score']:.2f} - {'✅' if r['faith_std']['success'] else '❌'}<br><sub>{r['faith_std']['reason']}</sub> | {r['faith_ver']['score']:.2f} - {'✅' if r['faith_ver']['success'] else '❌'}<br><sub>{r['faith_ver']['reason']}</sub> |\n")
            f.write(f"| **Hallucination** | {r['hallu_std']['score']:.2f} - {'✅' if r['hallu_std']['success'] else '❌'}<br><sub>{r['hallu_std']['reason']}</sub> | {r['hallu_ver']['score']:.2f} - {'✅' if r['hallu_ver']['success'] else '❌'}<br><sub>{r['hallu_ver']['reason']}</sub> |\n")
            f.write(f"| **Answer Relevancy** | {r['ans_rel_std']['score']:.2f} - {'✅' if r['ans_rel_std']['success'] else '❌'}<br><sub>{r['ans_rel_std']['reason']}</sub> | {r['ans_rel_ver']['score']:.2f} - {'✅' if r['ans_rel_ver']['success'] else '❌'}<br><sub>{r['ans_rel_ver']['reason']}</sub> |\n")
            f.write(f"| **Context Relevancy** | {r['ctx_rel_std']['score']:.2f} - {'✅' if r['ctx_rel_std']['success'] else '❌'}<br><sub>{r['ctx_rel_std']['reason']}</sub> | {r['ctx_rel_ver']['score']:.2f} - {'✅' if r['ctx_rel_ver']['success'] else '❌'}<br><sub>{r['ctx_rel_ver']['reason']}</sub> |\n")
            f.write(f"| **Context Precision** | {r['ctx_prec_std']['score']:.2f} - {'✅' if r['ctx_prec_std']['success'] else '❌'}<br><sub>{r['ctx_prec_std']['reason']}</sub> | {r['ctx_prec_ver']['score']:.2f} - {'✅' if r['ctx_prec_ver']['success'] else '❌'}<br><sub>{r['ctx_prec_ver']['reason']}</sub> |\n")
            f.write(f"| **Context Recall** | {r['ctx_recall_std']['score']:.2f} - {'✅' if r['ctx_recall_std']['success'] else '❌'}<br><sub>{r['ctx_recall_std']['reason']}</sub> | {r['ctx_recall_ver']['score']:.2f} - {'✅' if r['ctx_recall_ver']['success'] else '❌'}<br><sub>{r['ctx_recall_ver']['reason']}</sub> |\n\n")

            f.write("#### Responses\n")
            f.write("<details><summary><b>View Standard Response</b></summary>\n\n")
            f.write(f"```text\n{r['ans_std']}\n```\n")
            f.write("</details>\n\n")
            f.write("<details><summary><b>View Verified Response</b></summary>\n\n")
            f.write(f"```text\n{r['ans_ver']}\n```\n")
            if r['ver_text']:
                f.write(f"**PubMed Verification:**\n```text\n{r['ver_text']}\n```\n")
            f.write("</details>\n")
            f.write("\n---\n")

    print(f"\n[COMPLETED] Research report generated at: {report_path}")

def generate_global_comparison_report(all_model_results):
    timestamp = int(time.time())
    global_report_path = f"{REPORT_DIR}/GLOBAL_COMPARISON_REPORT_{timestamp}.md"
    
    with open(global_report_path, "w") as f:
        f.write("# Global Clinical RAG Benchmark: Model Comparison\n\n")
        f.write("| Model | Latency | Faithfulness | Hallucination | Answer Rel | Context Rel | Context Prec | Context Recall |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        
        for data in all_model_results:
            model = data["model"]
            reports = data["reports"]
            
            avg_lat_ver = sum(r['latency_ver'] for r in reports) / len(reports)
            
            def g(key):
                scores = [r[key]['score'] for r in reports]
                passes = [1 if r[key]['success'] else 0 for r in reports]
                return f"{sum(scores)/len(scores):.2f} ({(sum(passes)/len(passes))*100:.0f}%)"

            f_v = g('faith_ver')
            h_v = g('hallu_ver')
            ar_v = g('ans_rel_ver')
            cr_v = g('ctx_rel_ver')
            cp_v = g('ctx_prec_ver')
            cre_v = g('ctx_recall_ver')
            
            f.write(f"| **{model}** | {avg_lat_ver:.2f}s | {f_v} | {h_v} | {ar_v} | {cr_v} | {cp_v} | {cre_v} |\n")
            
        f.write("\n\n## Summary of Findings\n")
        f.write("This report compares the performance of five different LLMs across Standard and Verified RAG workflows. Verified RAG typically increases latency due to external PubMed searches but often improves clinical faithfulness and reduces hallucinations.\n")

    print(f"\n[GLOBAL REPORT] Comparison summary generated at: {global_report_path}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1].lower() == "all":
        print(f"Starting comprehensive benchmark for all models: {MODELS}")
        all_results = []
        for model in MODELS:
            try:
                reports = run_individual_bench(model)
                if reports:
                    all_results.append({"model": model, "reports": reports})
            except Exception as e:
                print(f"Error benchmarking model {model}: {e}")
        
        if all_results:
            generate_global_comparison_report(all_results)
    else:
        model = TARGET_MODEL
        if len(sys.argv) > 1:
            model = sys.argv[1]
        run_individual_bench(model)
