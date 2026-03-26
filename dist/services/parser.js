import fs from 'fs-extra';
import ndjson from 'ndjson';
export class ParserService {
    async *parseFile(filePath) {
        const stream = fs.createReadStream(filePath).pipe(ndjson.parse());
        for await (const obj of stream) {
            if (obj && typeof obj === 'object' && obj.resourceType) {
                yield obj;
            }
            else {
                console.warn(`Malformed line in ${filePath}:`, obj);
            }
        }
    }
    async listFiles(directoryPath) {
        const files = await fs.readdir(directoryPath);
        return files
            .filter(f => f.endsWith('.ndjson'))
            .map(f => `${directoryPath}/${f}`);
    }
}
