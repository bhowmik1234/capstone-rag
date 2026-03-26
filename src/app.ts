import express from 'express';
import cors from 'cors';
import morgan from 'morgan';
import { RetrievalService } from './services/retriever.js';
import { AnswerGeneratorService } from './services/generator.js';
import { VectorDbService } from './services/vectorDb.js';
import { OllamaService } from './services/ollama.js';
import { PubMedService } from './services/pubmed.js';
import { QueryRequest } from './types/index.js';

const app = express();
app.use(express.json());
app.use(cors());
app.use(morgan('dev'));

const vectorDb = new VectorDbService();
const ollama = new OllamaService();
const pubmed = new PubMedService();
const retriever = new RetrievalService(vectorDb, ollama);
const generator = new AnswerGeneratorService(ollama);

app.post('/query', async (req, res) => {
    try {
        const { question, patientId, patientName } = req.body as QueryRequest;

        if (!question) {
            return res.status(400).json({ error: 'Question is required' });
        }

        console.log(`Processing query: "${question}" for patient: ${patientId || patientName || 'ANY'}`);

        // Retrieval
        const { context, sources, intent, patientId: foundId, patientName: foundName } = await retriever.retrieve({
            question,
            patientId,
            patientName
        });

        if (!context) {
            return res.json({
                answer: "No relevant clinical records found for this query.",
                patient: { id: patientId || "unknown", name: patientName || "unknown" },
                intent,
                sources: [],
                warnings: ["No data retrieved from vector database"]
            });
        }

        // Generation
        const patientContext = `Patient ID: ${foundId || patientId || "unknown"}, Name: ${foundName || patientName || "unknown"}`;
        const { answer: initialAnswer, warnings } = await generator.generateAnswer(question, context, patientContext);

        // PubMed verification step
        console.log("Extracting search terms for PubMed...");
        const searchTerms = await generator.extractSearchTerms(question, initialAnswer);
        
        console.log(`Searching PubMed for: ${searchTerms}`);
        const pubMedArticles = await pubmed.searchAndFetchArticles(searchTerms, 3);
        
        console.log("Verifying and refining answer with PubMed...");
        const { finalAnswer, verification, articles } = await generator.verifyAndRefine(question, initialAnswer, pubMedArticles);

        res.json({
            answer: finalAnswer,
            verification,
            pubmedArticles: articles || [],
            patient: {
                id: foundId || patientId || "unknown",
                name: foundName || patientName || "unknown"
            },
            intent,
            sources,
            warnings
        });

    } catch (error: any) {
        console.error('Error handling query:', error);
        res.status(500).json({ error: 'Internal server error', details: error.message });
    }
});

export default app;
