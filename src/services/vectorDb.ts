import * as lancedb from '@lancedb/lancedb';
import { config } from '../config/index.js';
import { NormalizedRecord } from '../types/index.js';

export class VectorDbService {
    private db: lancedb.Connection | null = null;
    private tableName = 'fhir_resources';

    async connect() {
        if (!this.db) {
            this.db = await lancedb.connect(config.lanceDbPath);
        }
        return this.db;
    }

    async createTable(data: NormalizedRecord[]) {
        const db = await this.connect();
        return await db.createTable(this.tableName, data as any[], { mode: 'overwrite' });
    }

    async getTable() {
        const db = await this.connect();
        return await db.openTable(this.tableName);
    }

    async search(vector: number[], limit: number = 10, filter?: string) {
        const table = await this.getTable();
        let query = table.vectorSearch(vector).limit(limit);
        if (filter) {
            query = query.where(filter);
        }
        return await query.toArray();
    }
}
