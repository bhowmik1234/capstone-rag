import { RetrievalService } from '../services/retriever.js';
import { VectorDbService } from '../services/vectorDb.js';
import { OllamaService } from '../services/ollama.js';
import { config } from '../config/index.js';
import axios from 'axios';

async function runComparison() {
    console.log('--- Starting Model Comparison ---');
    console.log(`Hardware: Mac M2, 8GB RAM\n`);

    const modelsToTest = ['llama3.1', 'llama3.2:1b', 'llama3.2:3b', 'phi3:mini'];
    const testQueries = [
        {
            question: "What medications is the patient currently taking?",
            patientId: "129c6ac7-8d06-89de-ad63-0204a93e76c3"
        },
        {
            question: "What are the latest vitals for this patient?",
            patientId: "129c6ac7-8d06-89de-ad63-0204a93e76c3"
        },
        {
            question: "Does the patient have any history of respiratory conditions?",
            patientId: "129c6ac7-8d06-89de-ad63-0204a93e76c3"
        }
    ];

    const vectorDb = new VectorDbService();
    const ollama = new OllamaService();
    const retriever = new RetrievalService(vectorDb, ollama);

    const results: any[] = [];

    for (const model of modelsToTest) {
        console.log(`\nTesting Model: ${model}...`);
        
        // Update model in OllamaService (hacky but works for comparison)
        (ollama as any).chatModel = model;

        const modelResults = {
            model,
            queries: [] as any[]
        };

        for (const query of testQueries) {
            console.log(`  Query: "${query.question}"`);
            
            try {
                // 1. Retrieve context
                const { context } = await retriever.retrieve(query);

                const startTime = Date.now();
                
                // 2. Generate response using specific model
                const prompt = `Use the following medical context to answer the user's question safely and accurately. 
                If the information is not in the context, say you don't know based on the provided records.
                
                Context:
                ${context}
                
                Question: ${query.question}`;

                const response = await ollama.generateChatResponse(prompt, "You are a clinical assistant.");
                
                const endTime = Date.now();
                const duration = (endTime - startTime) / 1000;

                modelResults.queries.push({
                    question: query.question,
                    duration,
                    responseLength: response.length,
                    response: response.substring(0, 100) + '...'
                });

                console.log(`    Done in ${duration.toFixed(2)}s`);
            } catch (error: any) {
                console.error(`    Error testing model ${model}:`, error.message);
                modelResults.queries.push({
                    question: query.question,
                    error: error.message
                });
            }
        }
        results.push(modelResults);
    }

    // Output Summary
    console.log('\n\n--- Comparison Summary ---');
    console.table(results.map(r => ({
        Model: r.model,
        AvgLatency: (r.queries.reduce((acc: number, q: any) => acc + (q.duration || 0), 0) / r.queries.length).toFixed(2) + 's',
        Status: r.queries.every((q: any) => !q.error) ? '✅ Success' : '❌ Errors'
    })));

    console.log('\nDetailed results available in logs/comparison_results.json');
}

runComparison().catch(console.error);
