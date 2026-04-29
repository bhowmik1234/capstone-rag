import matplotlib.pyplot as plt
import numpy as np
import os

# Data
models = ['Llama 3.2 (3B)', 'Meditron (7B)', 'Nemotron-Mini (4B)']
latency_std = [15.71, 14.42, 8.24]
latency_ver = [35.62, 40.49, 28.07]
faith_std = [0.50, 0.53, 0.26]
faith_ver = [0.68, 0.53, 0.50]
hallu_std = [0.70, 0.50, 0.70]
hallu_ver = [0.70, 0.50, 0.30]

output_dir = 'benchmark_reports/graphs'
os.makedirs(output_dir, exist_ok=True)

# Plot 1: Latency Comparison
plt.figure(figsize=(10, 6))
x = np.arange(len(models))
width = 0.25
plt.bar(x - width, latency_std, width, label='Standard RAG', color='#3498db')
plt.bar(x, latency_ver, width, label='Verified RAG', color='#e74c3c')
plt.ylabel('Average Latency (seconds)')
plt.title('Latency Comparison: Standard vs Verified RAG')
plt.xticks(x, models)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(f'{output_dir}/latency_comparison.png')
plt.close()

# Plot 2: Faithfulness Comparison
plt.figure(figsize=(10, 6))
plt.bar(x - width, faith_std, width, label='Standard RAG', color='#2ecc71')
plt.bar(x, faith_ver, width, label='Verified RAG', color='#f1c40f')
plt.ylabel('Average Faithfulness Score')
plt.title('Faithfulness Comparison: Standard vs Verified RAG')
plt.xticks(x, models)
plt.ylim(0, 1.0)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(f'{output_dir}/faithfulness_comparison.png')
plt.close()

# Plot 3: Hallucination Comparison (New)
plt.figure(figsize=(10, 6))
plt.bar(x - width, hallu_std, width, label='Standard RAG', color='#95a5a6')
plt.bar(x, hallu_ver, width, label='Verified RAG', color='#9b59b6')
plt.ylabel('Average Hallucination Score (Lower is Better)')
plt.title('Hallucination Rate: Standard vs Verified RAG')
plt.xticks(x, models)
plt.ylim(0, 1.0)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(f'{output_dir}/hallucination_comparison.png')
plt.close()

# Plot 4: Trade-off (Latency vs Faithfulness)
plt.figure(figsize=(10, 6))
colors = ['#3498db', '#e74c3c', '#2ecc71']
for i, model in enumerate(models):
    plt.scatter(latency_ver[i], faith_ver[i], s=200, label=model, color=colors[i])
    plt.annotate(model, (latency_ver[i], faith_ver[i]), textcoords="offset points", xytext=(0,10), ha='center')

plt.xlabel('Average Latency (seconds)')
plt.ylabel('Verified Faithfulness Score')
plt.title('Clinical RAG Performance Trade-off (Verified Mode)')
plt.grid(linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig(f'{output_dir}/performance_tradeoff.png')
plt.close()

print(f"Graphs generated successfully in {output_dir}")
