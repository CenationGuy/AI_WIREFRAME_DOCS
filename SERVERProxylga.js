server.js

import 'dotenv/config';
import express from 'express';
import path from 'path';
import cors from 'cors';
import compression from 'compression';
import helmet from 'helmet';
import { GoogleAuth } from 'google-auth-library';
import { fileURLToPath } from 'url';

/**
 * --- CONFIGURATION ---
 */
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = process.env.PORT || 8080;
const EXPRESS_BACKEND_URL = process.env.EXPRESS_BACKEND_URL || "https://sac-commenting-api-374342742905.europe-west1.run.app";
const DIST_DIR = path.resolve(__dirname, 'dist');

// Optional: Base path (e.g. /my-app/)
const BASE_PATH = (process.env.PUBLIC_URL || '/').replace(/\/+$/, '') || '/';

console.log('--- Frontend Server Starting ---');
console.log(`Port: ${PORT}`);
console.log(`Backend: ${EXPRESS_BACKEND_URL}`);
console.log(`Static: ${DIST_DIR}`);
console.log(`Base Path: ${BASE_PATH}`);

const app = express();
const auth = new GoogleAuth();

/**
 * --- MIDDLEWARES ---
 */
app.set('trust proxy', 1); // Trust Cloud Run proxy

app.use(helmet({
    frameguard: false, // Allow embedding if needed
    contentSecurityPolicy: {
        directives: {
            ...helmet.contentSecurityPolicy.getDefaultDirectives(),
            "frame-ancestors": ["'self'", "*"], // Custom CSP for embedding
        },
    },
}));

app.use(cors());
app.use(compression());
app.use(express.json({ limit: '10mb' }));

// Request Logger
app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
    next();
});


/**
 * --- API PROXY LOGIC ---
 */
const proxyMiddleware = async (req, res) => {
    try {
        const targetUrl = `${EXPRESS_BACKEND_URL}${req.originalUrl.replace(BASE_PATH !== '/' ? BASE_PATH : '', '')}`;
        
        console.log(`[Proxy] Forwarding to: ${targetUrl}`);

        // Get GCP Identity Token for Service-to-Service auth
        const client = await auth.getIdTokenClient(EXPRESS_BACKEND_URL);
        const authHeaders = await client.getRequestHeaders();

        // Support both lowercase and TitleCase (library behavior varies by version)
        const identityToken = authHeaders.authorization || authHeaders.Authorization; 

        if (!identityToken) {
            console.error(`[Proxy Auth Warning] No identity token found for ${EXPRESS_BACKEND_URL}. Backend may reject request.`);
        }

        const bearerToken = identityToken 
            ? (identityToken.startsWith('Bearer ') ? identityToken : `Bearer ${identityToken}`)
            : '';

        // Extract clean email from GCP IAP header (Format: 'accounts.google.com:user@example.com')
        const gcpUserHeader = req.headers['x-goog-authenticated-user-email'] || '';
        const authenticatedEmail = gcpUserHeader ? gcpUserHeader.split(':').pop() : '';

        const response = await fetch(targetUrl, {
            method: req.method,
            headers: {
                'Content-Type': 'application/json',
                // Standard Authorization header for Cloud Run service-to-service
                ...(bearerToken && { 'Authorization': bearerToken }),
                // Secondary for backend custom logic if needed
                ...(bearerToken && { 'X-Serverless-Authorization': bearerToken }),
                // Forward the "purified" email to the backend
                'x-user-email': authenticatedEmail,
            },
            body: ['POST', 'PUT', 'PATCH'].includes(req.method) ? JSON.stringify(req.body) : undefined
        });

        const contentType = response.headers.get('content-type');
        res.status(response.status);

        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            res.json(data);
        } else {
            const text = await response.text();
            res.send(text);
        }
    } catch (error) {
        console.error(`[Proxy Error] ${req.url}:`, error.message);
        res.status(500).json({ 
            error: 'Backend unreachable or Auth failure',
            details: error.message 
        });
    }
};

// Mount proxy for any /api route
app.all(`${BASE_PATH === '/' ? '' : BASE_PATH}/api/*`, proxyMiddleware);
app.all('/api/*', proxyMiddleware); // Fallback for absolute /api hits

/**
 * --- STATIC FILES & SPA FALLBACK ---
 */
// Serve static assets with caching
app.use(BASE_PATH, express.static(DIST_DIR, {
    maxAge: '1y',
    immutable: true,
    index: false
}));

// Fallback for non-file requests (SPA Routing)
app.get('*', (req, res) => {
    // If it's a file request but wasn't caught by static middleware, it's 404
    if (path.extname(req.url)) {
        return res.status(404).send('Not Found');
    }
    
    // Otherwise, serve index.html for React Router to handle
    res.sendFile(path.join(DIST_DIR, 'index.html'));
});

/**
 * --- SERVER START ---
 */
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server listening on http://0.0.0.0:${PORT}`);
});



vite.config.js


import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './', // Use relative paths for embedding
  server: {
    proxy: {
      // Forward /api requests to your backend server
      '/api': {
        target: 'http://localhost:3000', // Change this to your backend server port
        changeOrigin: true,
      }
    }
  }
})



api.js

const API_BASE = '/api';



export async function fetchComments(): Promise<Comment[]> {

  try {
    const res = await fetch(`${API_BASE}/comment?${params}`, {
      cache: 'no-store', // Always get fresh 200 OK with full JSON payload
      headers: {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
      }
    });
    const data: Comment[] = await res.json();
    return data ?? [];
  } catch (err) {
    console.warn("fetchComments network error, trying cache:", err);
    const cached = localStorage.getItem(cacheKey);
    return cached ? (JSON.parse(cached) as Comment[]) : [];
  }
}
