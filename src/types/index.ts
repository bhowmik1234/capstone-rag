export interface FhirResource {
    resourceType: string;
    id: string;
    [key: string]: any;
}

export interface NormalizedRecord {
    id: string;
    patientId: string;
    patientName?: string;
    resourceType: string;
    resourceId: string;
    clinicalDate: string;
    category?: string;
    status?: string;
    textContent: string; // The normalized text for embeddings
    metadata: {
        originalResource: string;
        tags: string[];
        codeText?: string;
        display?: string;
    };
    vector?: number[];
}

export interface QueryRequest {
    question: string;
    patientId?: string;
    patientName?: string;
    retrievalStrategy?: 'bm25' | 'embedding' | 'hybrid';
}

export interface RetrievalSource {
    resourceType: string;
    resourceId: string;
    date: string;
    summary: string;
}

export interface QueryResponse {
    answer: string;
    patient: {
        id: string;
        name: string;
    };
    intent: string;
    sources: RetrievalSource[];
    warnings: string[];
}
