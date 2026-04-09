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

async function test() {
  try {
    await client.connect();
    console.log('✅ Connected\n');

    // Check available extensions
    console.log('📋 Available extensions:');
    const ext = await client.query(`
      SELECT name FROM pg_available_extensions 
      WHERE name IN ('uuid-ossp', 'vector', 'pgvector')
      ORDER BY name;
    `);
    console.log(ext.rows);

    // Check installed extensions
    console.log('\n📦 Installed extensions:');
    const inst = await client.query(`
      SELECT extname, extversion, nspname as schema
      FROM pg_extension e
      JOIN pg_namespace n ON e.extnamespace = n.oid
      ORDER BY extname;
    `);
    console.log(inst.rows);

    // Check schemas
    console.log('\n📁 Schemas:');
    const sch = await client.query(`
      SELECT schema_name FROM information_schema.schemata
      ORDER BY schema_name;
    `);
    console.log(sch.rows);

  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await client.end();
  }
}

test();
