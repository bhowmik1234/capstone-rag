export class AnswerGeneratorService {
    ollama;
    constructor(ollama) {
        this.ollama = ollama;
    }
    async generateAnswer(question, context, patientContext) {
        const prompt = `You are a healthcare record question-answering assistant.

Answer ONLY from the provided retrieved clinical evidence.
Do not use outside knowledge.
Do not hallucinate.
If the record does not contain enough evidence, say that clearly.
Prefer the latest clinically relevant records when the question asks about current, latest, or recent information.
Be precise, concise, and factual.
Mention dates when important.
Differentiate between active, historical, and unknown status when possible.
Do not infer a disease, allergy, or side effect unless it is directly supported by the evidence.

Return:
1. A direct answer
2. A short evidence summary
3. Any missing-data warning if needed

QUESTION:
${question}

PATIENT:
${patientContext}

RETRIEVED EVIDENCE:
${context}`;
        const answer = await this.ollama.generateChatResponse(prompt);
        // Identify warnings based on context presence
        const warnings = [];
        if (question.toLowerCase().includes('vital') && !context.toLowerCase().includes('observation')) {
            warnings.push('No Observation records found to answer vitals query.');
        }
        return {
            answer,
            warnings
        };
    }
    async extractSearchTerms(question, initialAnswer) {
        const prompt = `Based on the following patient clinical question and the initial answer derived from their records, extract 2-3 key medical terms (conditions, medications, or procedures) to search in PubMed for general medical verification.
        
        QUESTION: ${question}
        INITIAL ANSWER: ${initialAnswer}
        
        Return ONLY the search terms separated by spaces. Do not include patient names or IDs.
        Example: "asthma salbutamol treatment"`;
        const terms = await this.ollama.generateChatResponse(prompt, "You are a medical search assistant. Output only keywords.");
        return terms.trim().replace(/^"|"$/g, '');
    }
    async verifyAndRefine(question, initialAnswer, pubMedArticles) {
        if (pubMedArticles.length === 0) {
            return {
                finalAnswer: initialAnswer,
                verification: "No external PubMed articles found for cross-verification."
            };
        }
        const pubMedContext = pubMedArticles.map(a => `ID: ${a.id}\nTitle: ${a.title}\nSummary: ${a.abstract}`).join('\n\n');
        const prompt = `You are a medical verification assistant. 
        You are given an initial answer based on a patient's PRIVATE clinical records, and a set of PUBLIC medical articles from PubMed.

        INITIAL ANSWER:
        ${initialAnswer}

        PUBMED ARTICLES:
        ${pubMedContext}

        TASK:
        1. Verify if the medical facts in the initial answer (e.g., medication usage, treatment standards) align with the general medical knowledge in the PubMed articles.
        2. Provide a "nice, brief, and appropriate" final response that combines the patient-specific facts with a brief verification or context from PubMed.
        3. If there's a conflict or if the PubMed articles suggest something important that's relevant to the patient's context, mention it gently as a general medical note.
        4. Focus on being professional and helpful.

        Structure your response as:
        - FINAL RESPONSE: [The refined answer]
        - PUBMED VERIFICATION: [A brief sentence about the verification against literature]`;
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
