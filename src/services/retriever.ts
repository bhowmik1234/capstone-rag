import { VectorDbService } from './vectorDb.js';
import { OllamaService } from './ollama.js';
import { BM25 } from './bm25.js';
import { QueryRequest, RetrievalSource } from '../types/index.js';

export class RetrievalService {
    private vectorDb: VectorDbService;
    private ollama: OllamaService;

    constructor(vectorDb: VectorDbService, ollama: OllamaService) {
        this.vectorDb = vectorDb;
        this.ollama = ollama;
    }

    async retrieve(request: QueryRequest) {
        const { question, patientId, patientName, retrievalStrategy = 'hybrid' } = request;

        //  Detect Intent
        const intent = this.detectIntent(question);

        //  Build Filter
        let filterParts = [];
        if (patientId) {
            filterParts.push(`patientId = '${patientId}'`);
        } else if (patientName) {
            filterParts.push(`patientName = '${patientName}'`);
        }

        // Route by intent to specific resource types
        const resourceTypes = this.getResourceTypesForIntent(intent);
        if (resourceTypes.length > 0) {
            const typeFilter = resourceTypes.map(t => `resourceType = '${t}'`).join(' OR ');
            filterParts.push(`(${typeFilter})`);
        }

        const filter = filterParts.length > 0 ? filterParts.join(' AND ') : undefined;
        let results: any[] = [];

        if (retrievalStrategy === 'embedding') {
            const queryVector = await this.ollama.generateEmbedding(question);
            results = await this.vectorDb.search(queryVector, 15, filter);
        } else if (retrievalStrategy === 'bm25') {
            const allRecords = await this.vectorDb.getRecords(filter);
            if (allRecords.length > 0) {
                const bm25 = new BM25();
                bm25.fit(allRecords.map((r: any) => r.textContent));
                const scores = bm25.score(question);
                
                const scoredRecords = allRecords.map((r: any, idx: number) => ({ ...r, _score: scores[idx] }));
                scoredRecords.sort((a, b) => b._score - a._score);
                results = scoredRecords.slice(0, 15);
            }
        } else { // hybrid
            const queryVector = await this.ollama.generateEmbedding(question);
            const candidateRecords = await this.vectorDb.search(queryVector, 100, filter);
            if (candidateRecords.length > 0) {
                const bm25 = new BM25();
                bm25.fit(candidateRecords.map((r: any) => r.textContent));
                const bm25Scores = bm25.score(question);

                const maxBm25 = Math.max(...bm25Scores, 0.0001);
                const minBm25 = Math.min(...bm25Scores);
                const bm25Range = maxBm25 - minBm25 > 0 ? maxBm25 - minBm25 : 1;

                const distances = candidateRecords.map((r: any) => r._distance || 0);
                const maxDist = Math.max(...distances, 0.0001);
                const minDist = Math.min(...distances);
                const distRange = maxDist - minDist > 0 ? maxDist - minDist : 1;

                const alpha = 0.5;

                const hybridRecords = candidateRecords.map((r: any, idx: number) => {
                    const normBm25 = (bm25Scores[idx] - minBm25) / bm25Range;
                    const normEmbedding = 1 - ((r._distance || 0) - minDist) / distRange;
                    const hybridScore = alpha * normBm25 + (1 - alpha) * normEmbedding;
                    return { ...r, _score: hybridScore };
                });

                hybridRecords.sort((a, b) => b._score - a._score);
                results = hybridRecords.slice(0, 15);
            }
        }

        // Re-rank/Sort by date for "latest" queries
        if (question.toLowerCase().match(/latest|current|recent|now/)) {
            results.sort((a: any, b: any) => new Date(b.clinicalDate).getTime() - new Date(a.clinicalDate).getTime());
        }

        // Format sources
        const sources: RetrievalSource[] = results.map((r: any) => ({
            resourceType: r.resourceType,
            resourceId: r.resourceId,
            date: r.clinicalDate,
            summary: r.textContent
        }));

        // Assemble context
        const context = results.map((r: any) => r.textContent).join('\n---\n');

        return {
            context,
            sources,
            intent,
            patientId: results[0]?.patientId || patientId,
            patientName: results[0]?.patientName || patientName
        };
    }

    private detectIntent(question: string): string {
        const q = question.toLowerCase();
        if (q.includes('vital') || q.includes('blood pressure') || q.includes('heart rate') || q.includes('temperature')) return 'vitals';
        if (q.includes('condition') || q.includes('disease') || q.includes('diagnosis') || q.includes('sick')) return 'diagnosis';
        if (q.includes('allergy') || q.includes('intolerance')) return 'allergy';
        if (q.includes('medication') || q.includes('medicine') || q.includes('drug') || q.includes('taking')) return 'medication';
        if (q.includes('procedure') || q.includes('surgery') || q.includes('operation')) return 'procedure';
        if (q.includes('side effect')) return 'side_effects';
        return 'general_clinical_inquiry';
    }

    private getResourceTypesForIntent(intent: string): string[] {
        switch (intent) {
            case 'vitals': return ['Observation'];
            case 'diagnosis': return ['Condition'];
            case 'allergy': return ['AllergyIntolerance'];
            case 'medication': return ['MedicationRequest'];
            case 'procedure': return ['Procedure'];
            case 'side_effects': return ['Observation', 'Condition', 'AllergyIntolerance', 'DiagnosticReport', 'MedicationRequest'];
            default: return [];
        }
    }
}
