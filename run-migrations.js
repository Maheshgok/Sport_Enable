import pg from 'pg';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const { Client } = pg;
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const client = new Client({
  host: 'localhost',
  port: 5432,
  database: 'moove_production',
  user: 'postgres',
  password: 'MooveSecure2026!',
  connectionTimeoutMillis: 30000
});

const sqlFiles = [
  'database/init.sql',
  'database/schema/01_users_and_profiles.sql',
  'database/schema/02_relationships.sql',
  'database/schema/03_clinical_data.sql',
  'database/schema/04_access_control.sql',
  'database/schema/05_sample_data.sql'
];

async function runMigrations() {
  try {
    console.log('Connecting to database...');
    await client.connect();
    console.log('✅ Connected\n');

    // Set search path for the session
    await client.query('SET search_path TO physio_app, public;');

    for (const file of sqlFiles) {
      const fileName = path.basename(file);
      console.log(`📄 Running: ${fileName}`);
      
      try {
        const sql = fs.readFileSync(file, 'utf8');
        await client.query(sql);
        console.log(`  ✅ Success\n`);
      } catch (error) {
        console.error(`  ❌ Error in ${fileName}:`);
        console.error(`  ${error.message}\n`);
        // Continue with other files even if one fails
      }
    }

    console.log('Migration complete!');
    
  } catch (error) {
    console.error('Connection error:', error.message);
  } finally {
    await client.end();
  }
}

runMigrations();
