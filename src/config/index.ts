import dotenv from 'dotenv';
import path from 'path';

dotenv.config();

export const config = {
    port: parseInt(process.env.PORT || '3000', 10),
    nodeEnv: process.env.NODE_ENV || 'development',
    dataDir: path.resolve(process.env.DATA_DIR || './data'),
    lanceDbPath: path.resolve(process.env.LANCE_DB_PATH || './data/fhir_vectors'),
    fhirDatasetPath: process.env.FHIR_DATASET_PATH || '',
    ollama: {
        baseUrl: process.env.OLLAMA_BASE_URL || 'http://localhost:11434',
        embeddingModel: process.env.EMBEDDING_MODEL || 'nomic-embed-text',
        chatModel: process.env.CHAT_MODEL || 'llama3.1',
    },
    logLevel: process.env.LOG_LEVEL || 'info',
};
