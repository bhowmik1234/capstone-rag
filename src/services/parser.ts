import fs from 'fs-extra';
import ndjson from 'ndjson';
import { FhirResource } from '../types/index.js';

export class ParserService {
    async *parseFile(filePath: string): AsyncGenerator<FhirResource> {
        const stream = fs.createReadStream(filePath).pipe(ndjson.parse());

        for await (const obj of stream) {
            if (obj && typeof obj === 'object' && obj.resourceType) {
                yield obj as FhirResource;
            } else {
                console.warn(`Malformed line in ${filePath}:`, obj);
            }
        }
    }

    async listFiles(directoryPath: string): Promise<string[]> {
        const files = await fs.readdir(directoryPath);
        return files
            .filter(f => f.endsWith('.ndjson'))
            .map(f => `${directoryPath}/${f}`);
    }
}
