import { VectorDbService } from './vectorDb.js';
import { OllamaService } from './ollama.js';
import { QueryRequest, RetrievalSource } from '../types/index.js';

export class RetrievalService {
    private vectorDb: VectorDbService;
    private ollama: OllamaService;

    constructor(vectorDb: VectorDbService, ollama: OllamaService) {
        this.vectorDb = vectorDb;
        this.ollama = ollama;
    }

    async retrieve(request: QueryRequest) {
        const { question, patientId, patientName } = request;

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

        // Generate query embedding
        const queryVector = await this.ollama.generateEmbedding(question);

        // Search Vector DB
        const results = await this.vectorDb.search(queryVector, 15, filter);

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
