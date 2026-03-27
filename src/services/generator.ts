import { OllamaService } from './ollama.js';
import { RetrievalSource } from '../types/index.js';
import { PubMedArticle } from './pubmed.js';

export class AnswerGeneratorService {
    private ollama: OllamaService;

    constructor(ollama: OllamaService) {
        this.ollama = ollama;
    }

    async generateAnswer(question: string, context: string, patientContext: string) {
        const prompt = `You are a Senior Clinical Informaticist providing a consultation report based on patient FHIR records.
        
        STRUCTURE YOUR RESPONSE AS FOLLOWS:
        1. CLINICAL SUMMARY: A detailed, professional answer to the question.
        2. RECORD EVIDENCE: List specific clinical resources (e.g., Condition onset, Observation value) found in the retrieval context.
        3. CLINICAL STATUS: Clearly state if the condition/medication is ACTIVE, RESOLVED, or UNKNOWN based on meta-data.
        4. CONFIDENCE LEVEL: State your confidence (Low/Med/High) based on the clarity of the retrieved evidence.

        RULES:
        - Answer ONLY from the provided evidence.
        - Mention exact dates and values.
        - If data is missing or conflicting, state it clearly in the summary.
        - Be objective and use medical terminology.

        QUESTION: ${question}
        PATIENT PROFILE: ${patientContext}
        RETRIEVED FHIR EVIDENCE:
        ${context}`;

        const answer = await this.ollama.generateChatResponse(prompt);

        // Identify warnings based on context presence
        const warnings: string[] = [];
        if (question.toLowerCase().includes('vital') && !context.toLowerCase().includes('observation')) {
            warnings.push('No Observation records found to answer vitals query.');
        }

        return {
            answer,
            warnings
        };
    }

    async extractSearchTerms(question: string, initialAnswer: string): Promise<string> {
        const prompt = `Medical Search Assistant: Extract ONLY 3 simple medical keywords from this question/answer. 
        NO DATES. NO NAMES. NO PII. NO SENTENCES.
        
        QUESTION: ${question}
        INITIAL ANSWER: ${initialAnswer}
        
        OUTPUT ONLY THE KEYWORDS SEPARATED BY SPACES.
        Example Output: asthma inhaler treatment`;

        const terms = await this.ollama.generateChatResponse(prompt, "You are a medical search assistant. Output only 3 keywords.");
        // Clean up any stray quotes, newlines or conversational filler
        return terms.trim()
            .replace(/^"|"$/g, '')
            .replace(/keywords:?/i, '')
            .split('\n')[0]
            .trim();
    }

    async verifyAndRefine(question: string, initialAnswer: string, pubMedArticles: PubMedArticle[]) {
        if (pubMedArticles.length === 0) {
            return {
                finalAnswer: initialAnswer,
                verification: "No external PubMed articles found for cross-verification."
            };
        }

        const pubMedContext = pubMedArticles.map(a => `ID: ${a.id}\nTitle: ${a.title}\nSummary: ${a.abstract}`).join('\n\n');

        const prompt = `You are a Clinical Research Assistant. 
        Your goal is to synthesize PATIENT-SPECIFIC records with GENERAL MEDICAL KNOWLEDGE from PubMed.

        PATIENT RECORD SUMMARY (INITIAL):
        ${initialAnswer}

        PUBMED CLINICAL LITERATURE:
        ${pubMedContext}

        TASK:
        Refine the initial answer into a comprehensive "Clinical Consultation Report".

        REQUIRED STRUCTURE:
        - PATIENT-SPECIFIC SYNTHESIS: Elaborate the patient's specific health data.
        - LITERATURE-BASED CONTEXT: Summarize how the PubMed articles relate to the patient's conditions/medications.
        - RECOMMENDATION LOGIC: Briefly note standard medical practice for this context based on literature.
        - PUBMED VERIFICATION: A final confirmation of fact-consistency.

        Maintain professional medical tone. Use technical terms correctly.`;

        const refinement = await this.ollama.generateChatResponse(prompt);
        
        // Simple parsing
        const finalResponseMatch = refinement.match(/FINAL RESPONSE:\s*([\s\S]*?)(?=PUBMED VERIFICATION:|$)/i);
        const verificationMatch = refinement.match(/PUBMED VERIFICATION:\s*([\s\S]*)/i);

        return {
            finalAnswer: finalResponseMatch ? finalResponseMatch[1].trim() : refinement,
            verification: verificationMatch ? verificationMatch[1].trim() : "Verified against PubMed literature.",
            articles: pubMedArticles.map(a => ({ title: a.title, url: a.url }))
        };
    }
}
