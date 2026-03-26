export class RetrievalService {
    vectorDb;
    ollama;
    constructor(vectorDb, ollama) {
        this.vectorDb = vectorDb;
        this.ollama = ollama;
    }
    async retrieve(request) {
        const { question, patientId, patientName } = request;
        // 1. Detect Intent
        const intent = this.detectIntent(question);
        // 2. Build Filter
        let filterParts = [];
        if (patientId) {
            filterParts.push(`patientId = '${patientId}'`);
        }
        else if (patientName) {
            filterParts.push(`patientName = '${patientName}'`);
        }
        // Optional: Route by intent to specific resource types
        const resourceTypes = this.getResourceTypesForIntent(intent);
        if (resourceTypes.length > 0) {
            const typeFilter = resourceTypes.map(t => `resourceType = '${t}'`).join(' OR ');
            filterParts.push(`(${typeFilter})`);
        }
        const filter = filterParts.length > 0 ? filterParts.join(' AND ') : undefined;
        // 3. Generate query embedding
        const queryVector = await this.ollama.generateEmbedding(question);
        // 4. Search Vector DB
        const results = await this.vectorDb.search(queryVector, 15, filter);
        // 5. Re-rank/Sort by date for "latest" queries
        if (question.toLowerCase().match(/latest|current|recent|now/)) {
            results.sort((a, b) => new Date(b.clinicalDate).getTime() - new Date(a.clinicalDate).getTime());
        }
        // 6. Format sources
        const sources = results.map((r) => ({
            resourceType: r.resourceType,
            resourceId: r.resourceId,
            date: r.clinicalDate,
            summary: r.textContent
        }));
        // 7. Assemble context
        const context = results.map((r) => r.textContent).join('\n---\n');
        return {
            context,
            sources,
            intent,
            patientId: results[0]?.patientId || patientId,
            patientName: results[0]?.patientName || patientName
        };
    }
    detectIntent(question) {
        const q = question.toLowerCase();
        if (q.includes('vital') || q.includes('blood pressure') || q.includes('heart rate') || q.includes('temperature'))
            return 'vitals';
        if (q.includes('condition') || q.includes('disease') || q.includes('diagnosis') || q.includes('sick'))
            return 'diagnosis';
        if (q.includes('allergy') || q.includes('intolerance'))
            return 'allergy';
        if (q.includes('medication') || q.includes('medicine') || q.includes('drug') || q.includes('taking'))
            return 'medication';
        if (q.includes('procedure') || q.includes('surgery') || q.includes('operation'))
            return 'procedure';
        if (q.includes('side effect'))
            return 'side_effects';
        return 'general_clinical_inquiry';
    }
    getResourceTypesForIntent(intent) {
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
