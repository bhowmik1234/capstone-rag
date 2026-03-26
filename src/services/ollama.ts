import axios from 'axios';
import { config } from '../config/index.js';

export class OllamaService {
    private baseUrl: string;
    private embeddingModel: string;
    private chatModel: string;

    constructor() {
        this.baseUrl = config.ollama.baseUrl;
        this.embeddingModel = config.ollama.embeddingModel;
        this.chatModel = config.ollama.chatModel;
    }

    async generateEmbedding(text: string): Promise<number[]> {
        try {
            const response = await axios.post(`${this.baseUrl}/api/embeddings`, {
                model: this.embeddingModel,
                prompt: text,
            });
            return (response.data as any).embedding;
        } catch (error: any) {
            const errorMsg = error.response?.data?.error || error.message;
            console.error(`Error generating embedding (${this.embeddingModel}):`, errorMsg);
            throw new Error(`Embedding generation failed: ${errorMsg}`);
        }
    }

    async generateChatResponse(prompt: string, systemPrompt?: string): Promise<string> {
        try {
            const response = await axios.post(`${this.baseUrl}/api/generate`, {
                model: this.chatModel,
                prompt: prompt,
                system: systemPrompt,
                stream: false,
                options: {
                    temperature: 0.1, // Clinical grounding - keep it deterministic
                }
            });
            return (response.data as any).response;
        } catch (error: any) {
            console.error('Error generating chat response:', error.message);
            throw error;
        }
    }
}
