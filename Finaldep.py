sever.js

import "dotenv/config";
import express from "express";
import path from "path";
import multer from "multer";
import { GoogleAuth } from "google-auth-library";
import { fileURLToPath } from "url";

const app = express();

const PORT = process.env.PORT || 8080;

const FAST_API_URL =
  process.env.FAST_API_URL ||
  "https://ai-wireframe-backend-124794788198.europe-west1.run.app";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DIST_DIR = path.join(__dirname, "dist");

// Google authentication
const auth = new GoogleAuth();

// File upload configuration
const upload = multer({
  storage: multer.memoryStorage(),
});

// Middleware
app.use(express.json());

// Health check
app.get("/health", (req, res) => {
  res.json({
    status: "ok",
    service: "ai-wireframe-frontend",
  });
});

// API proxy
app.post(
  "/api/generate-dashboard",
  upload.single("file"),
  async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({
          detail: "CSV file is required.",
        });
      }

      console.log("Received file:", req.file.originalname);

      // Create authenticated Google client
      const client = await auth.getIdTokenClient(FAST_API_URL);

      const authHeaders = await client.getRequestHeaders();

      // Create multipart form
      const formData = new FormData();

      const blob = new Blob(
        [req.file.buffer],
        {
          type: req.file.mimetype || "text/csv",
        }
      );

      formData.append(
        "file",
        blob,
        req.file.originalname
      );

      // Forward request to FastAPI
      const response = await fetch(
        `${FAST_API_URL}/generate-dashboard`,
        {
          method: "POST",

          headers: {
            Authorization:
              authHeaders.Authorization ||
              authHeaders.authorization,
          },

          body: formData,
        }
      );

      const responseText = await response.text();

      let data;

      try {
        data = JSON.parse(responseText);
      } catch {
        data = {
          detail: responseText,
        };
      }

      if (!response.ok) {
        return res.status(response.status).json(data);
      }

      return res.json(data);

    } catch (error) {
      console.error("Proxy error:", error);

      return res.status(500).json({
        detail:
          "Backend unreachable or authentication failed.",
      });
    }
  }
);

// Serve React static files
app.use(express.static(DIST_DIR));

// React fallback
app.get("/{*splat}", (req, res) => {
  res.sendFile(path.join(DIST_DIR, "index.html"));
});

// Start server
app.listen(PORT, "0.0.0.0", () => {
  console.log(
    `Frontend server running on port ${PORT}`
  );
});
