import * as lancedb from '@lancedb/lancedb';
import { config } from './config/index.js';

async function verify() {
    const db = await lancedb.connect(config.lanceDbPath);
    const table = await db.openTable('fhir_resources');
    const count = await table.countRows();
    console.log(`Verification: Found ${count} rows in table 'fhir_resources'.`);
}

verify().catch(console.error);
