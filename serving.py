import express from 'express';
import path from 'path';
import helmet from 'helmet';
import dotenv from 'dotenv';
import cors from 'cors';
import { GoogleAuth } from 'google-auth-library';
import { PubSub } from '@google-cloud/pubsub';
import { BigQuery } from '@google-cloud/bigquery';
import crypto from 'crypto';

dotenv.config();

const FAST_API_URL = process.env.FAST_API_URL;
const PORT = process.env.PORT || 8080;
const PUBLIC_URL = process.env.PUBLIC_URL || '/vf-grp-aib-prd-mc2-sai-lab/iot-agent-dev-frontend/';
const PROJECT_ID = process.env.GOOGLE_CLOUD_PROJECT || 'vf-grp-aib-prd-mc2-sai-lab';
const TOPIC_NAME = process.env.PUBSUB_TOPIC || 'vf-grp-aib-prd-mc2-sai-lab-topic';
const TABLE_ID = process.env.BQ_TABLE_ID || 'vf-grp-datahub.vfgrp_dh_lake_iot_sales_agent_lab_s.leads';

// Base route WITHOUT trailing slash for Express static built-in redirect behavior
const baseRoute = '/' + PUBLIC_URL.replace(/^\/+|\/+$/g, '');
const DIST_DIR = path.join(import.meta.dirname, 'dist');

const app = express();
const auth = new GoogleAuth();
const pubsub = new PubSub({ projectId: PROJECT_ID });
const bigquery = new BigQuery({ projectId: PROJECT_ID, location: 'europe-west1' });

// Trust the first proxy (Cloud Run/Cloud Shell)
app.set('trust proxy', 1);

console.log('--- Production Server Starting (Simplified) ---');
console.log(`DIST_DIR: ${DIST_DIR}`);
console.log(`Base Route: ${baseRoute}`);
console.log(`FastAPI URL: ${FAST_API_URL}`);
console.log(`Project ID: ${PROJECT_ID}`);
console.log(`Topic Name: ${TOPIC_NAME}`);
console.log(`Table ID: ${TABLE_ID}`);

// Basic security and setup
app.use(helmet({ contentSecurityPolicy: false }));
app.use(cors());
app.use(express.json());

// Request Logger
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

// API Proxying Logic
const apiRouter = express.Router();
apiRouter.get('/health', (req, res) => res.json({ status: 'ok', source: 'node-server-prod' }));

const proxyToFastAPI = (targetPath) => async (req, res) => {
  try {
    const client = await auth.getIdTokenClient(FAST_API_URL);
    const authHeaders = await client.getRequestHeaders();
    const identityToken = authHeaders.authorization || authHeaders.get?.('authorization');

    const response = await fetch(`${FAST_API_URL}${targetPath}`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'X-Serverless-Authorization': identityToken 
      },
      body: JSON.stringify(req.body)
    });

    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error(`Proxy Error (${targetPath}):`, error);
    res.status(500).json({ error: 'Backend unreachable or Auth failure' });
  }
};

apiRouter.post('/url-extractor', proxyToFastAPI('/url-extractor'));
apiRouter.post('/lookalikes', proxyToFastAPI('/generate-leads'));
apiRouter.post('/filter-leads', proxyToFastAPI('/filter-leads'));

// Pub/Sub Enrichment Logic
apiRouter.post('/start-enrichment', async (req, res) => {
  try {
    const { names, config = {} } = req.body;
    if (!names || !Array.isArray(names)) {
      return res.status(400).json({ error: 'Invalid names list' });
    }

    const jobId = crypto.randomUUID();
    console.log(`Starting Enrichment Job ${jobId} for ${names.length} leads`);

    const topic = pubsub.topic(TOPIC_NAME);
    const publishPromises = names.map(name => {
      const data = {
        job_id: jobId,
        lead: { name },
        config: config
      };
      return topic.publishMessage({ json: data });
    });

    await Promise.all(publishPromises);
    res.json({ job_id: jobId, status: 'started', total: names.length });
  } catch (error) {
    console.error('Error starting enrichment:', error);
    res.status(500).json({ error: 'Failed to start enrichment job' });
  }
});

apiRouter.get('/enrichment-status/:job_id', async (req, res) => {
  try {
    const { job_id } = req.params;
    console.log(`Checking status for Job ID: ${job_id}`);

    const query = `
      SELECT name
      FROM \`${TABLE_ID}\`
      WHERE job_id = @jobId
    `;
    const options = {
      query: query,
      params: { jobId: job_id },
      location: 'europe-west1'
    };

    const [rows] = await bigquery.query(options);
    const leads = rows.map(row => row.name);
    
    res.json({
      job_id,
      count: leads.length,
      leads: leads
    });
  } catch (error) {
    console.error('Error fetching enrichment status:', error);
    res.status(500).json({ error: 'Failed to fetch status' });
  }
});

// API Mount (Dual-mount for maximum resilience against Load Balancer prefixing)
app.use(`${baseRoute}/api`, apiRouter);
app.use('/api', apiRouter);

// 1. Static Assets (Serve from both to handle prefix stripping/doubling)
app.use(baseRoute, express.static(DIST_DIR, { immutable: true, maxAge: '1y' }));
app.use('/', express.static(DIST_DIR, { immutable: true, maxAge: '1y' }));

// 2. Explicit Trailing Slash Redirect
// If user hits /prefix, redirect to /prefix/ so React Router basename works
if (baseRoute !== '' && baseRoute !== '/') {
  app.get(baseRoute, (req, res) => {
    console.log(`[Redirect] Enforcing trailing slash: ${req.url} -> ${baseRoute}/`);
    res.redirect(301, baseRoute + '/');
  });
}

// 3. Brute-Force SPA Routes (Deep Linking Fix)
// Map known routes explicitly so the server knows they are navigation, not files.
const knownRoutes = ['Overview', 'Discovery', 'Leads', 'Settings', 'Analysis'];

knownRoutes.forEach(route => {
  const handler = (req, res) => {
    console.log(`[SPA Brute-Force] Serving index.html for: ${req.url}`);
    res.sendFile(path.join(DIST_DIR, 'index.html'));
  };
  
  // Register for both prefixed and non-prefixed paths
  app.get(`${baseRoute}/${route}`, handler);
  app.get(`/${route}`, handler);
});

// 4. Global SPA Fallback (Final Safety Net)
app.get('*path', (req, res) => {
  // If it's a file request (e.g. .css, .js), but we reached here, it's missing.
  const isFile = path.extname(req.url) !== '';
  if (isFile) {
    console.log(`[404] Missing File: ${req.url}`);
    return res.status(404).send('Asset not found');
  }

  console.log(`[SPA Fallback] Serving index.html for unknown path: ${req.url}`);
  res.sendFile(path.join(DIST_DIR, 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server listening on port ${PORT}`);
  console.log(`App URL: http://0.0.0.0:${PORT}${baseRoute}/`);
});




 const auth = new GoogleAuth();








 import { GoogleAuth } from 'google-auth-library';



const proxyToFastAPI = (targetPath) => async (req, res) => {

  try {

    const client = await auth.getIdTokenClient(FAST_API_URL);

    const authHeaders = await client.getRequestHeaders();

    const identityToken = authHeaders.authorization || authHeaders.get?.('authorization');



    const response = await fetch(`${FAST_API_URL}${targetPath}`, {

      method: 'POST',

      headers: {

        'Content-Type': 'application/json',

        'X-Serverless-Authorization': identityToken

      },

      body: JSON.stringify(req.body)

    });



    const data = await response.json();

    res.json(data);

  } catch (error) {

    console.error(`Proxy Error (${targetPath}):`, error);

    res.status(500).json({ error: 'Backend unreachable or Auth failure' });

  }

};
