import axios from 'axios';
import { config } from '../config/index.js';
export class OllamaService {
    baseUrl;
    embeddingModel;
    chatModel;
    constructor() {
        this.baseUrl = config.ollama.baseUrl;
        this.embeddingModel = config.ollama.embeddingModel;
        this.chatModel = config.ollama.chatModel;
    }
    async generateEmbedding(text) {
        try {
            const response = await axios.post(`${this.baseUrl}/api/embeddings`, {
                model: this.embeddingModel,
                prompt: text,
            });
            return response.data.embedding;
        }
        catch (error) {
            const errorMsg = error.response?.data?.error || error.message;
            console.error(`Error generating embedding (${this.embeddingModel}):`, errorMsg);
            throw new Error(`Embedding generation failed: ${errorMsg}`);
        }
    }
    async generateChatResponse(prompt, systemPrompt) {
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
            return response.data.response;
        }
        catch (error) {
            console.error('Error generating chat response:', error.message);
            throw error;
        }
    }
}
