import pg from 'pg';
const { Client } = pg;

const client = new Client({
  host: 'localhost',
  port: 5432,
  database: 'moove_production',
  user: 'postgres',
  password: 'MooveSecure2026!',
  connectionTimeoutMillis: 30000
});

async function resetSchema() {
  try {
    await client.connect();
    console.log('✅ Connected\n');

    console.log('🗑️  Dropping physio_app schema...');
    await client.query('DROP SCHEMA IF EXISTS physio_app CASCADE;');
    console.log('✅ Schema dropped\n');

  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await client.end();
  }
}

resetSchema();
