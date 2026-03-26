import * as lancedb from '@lancedb/lancedb';
import { config } from '../config/index.js';
export class VectorDbService {
    db = null;
    tableName = 'fhir_resources';
    async connect() {
        if (!this.db) {
            this.db = await lancedb.connect(config.lanceDbPath);
        }
        return this.db;
    }
    async createTable(data) {
        const db = await this.connect();
        return await db.createTable(this.tableName, data, { mode: 'overwrite' });
    }
    async getTable() {
        const db = await this.connect();
        return await db.openTable(this.tableName);
    }
    async search(vector, limit = 10, filter) {
        const table = await this.getTable();
        let query = table.vectorSearch(vector).limit(limit);
        if (filter) {
            query = query.where(filter);
        }
        return await query.toArray();
    }
}
