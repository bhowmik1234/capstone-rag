import { ParserService } from '../services/parser.js';
import { NormalizerService } from '../services/normalizer.js';
import { OllamaService } from '../services/ollama.js';
import { VectorDbService } from '../services/vectorDb.js';
import { config } from '../config/index.js';
import path from 'path';
async function main() {
    console.log('Starting ingestion pipeline...');
    const parser = new ParserService();
    const normalizer = new NormalizerService();
    const ollama = new OllamaService();
    const vectorDb = new VectorDbService();
    const files = await parser.listFiles(config.fhirDatasetPath);
    console.log(`Found ${files.length} NDJSON files.`);
    const allRecords = [];
    const patientMap = {};
    // First pass to find all patients and map IDs to Names
    for (const file of files) {
        if (path.basename(file).toLowerCase().startsWith('patient.')) {
            console.log(`Processing patient file: ${file}`);
            for await (const resource of parser.parseFile(file)) {
                // console.log(`Normalizing patient: ${resource.id}`);
                const normalized = normalizer.normalize(resource);
                if (normalized && normalized.resourceType === 'Patient') {
                    patientMap[normalized.patientId] = normalized.patientName || 'Unknown';
                    // console.log(`Mapped patient ${normalized.patientId} to ${normalized.patientName}`);
                }
            }
        }
    }
    console.log(`Found ${Object.keys(patientMap).length} patients.`);
    // Second pass: Process all files and enrich with patient names
    for (const file of files) {
        if (file.toLowerCase().includes('log.ndjson'))
            continue;
        console.log(`Ingesting file: ${file}`);
        let fileCount = 0;
        for await (const resource of parser.parseFile(file)) {
            const normalized = normalizer.normalize(resource);
            if (normalized) {
                fileCount++;
                if (!normalized.patientName && normalized.patientId) {
                    normalized.patientName = patientMap[normalized.patientId] || 'Unknown';
                }
                // console.log(`Generating embedding for ${normalized.id}...`);
                try {
                    normalized.vector = await ollama.generateEmbedding(normalized.textContent);
                    allRecords.push(normalized);
                }
                catch (error) {
                    console.error(`Failed to generate embedding for ${normalized.id}: ${error.message}`);
                }
            }
        }
        console.log(`Added ${fileCount} records from ${file}`);
    }
    console.log(`Total records to ingest: ${allRecords.length}`);
    if (allRecords.length > 0) {
        await vectorDb.createTable(allRecords);
        console.log('Ingestion complete!');
    }
    else {
        console.error('No records found to ingest. Check data format and normalizer logic.');
    }
}
main().catch(console.error);
