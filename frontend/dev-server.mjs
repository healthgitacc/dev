// Simple development server workaround for Next.js path issues
import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import axios from 'axios';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;
const API_URL = 'http://localhost:8000';

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// API Proxy
app.use('/api', async (req, res) => {
  try {
    const response = await axios({
      method: req.method,
      url: `${API_URL}/api${req.path}`,
      data: req.body,
      headers: {
        ...req.headers,
        host: undefined,
      },
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json(error.response?.data || { error: 'Server error' });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', frontend: 'running' });
});

// Serve index.html for all other routes (SPA)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`✓ Frontend development server running at http://localhost:${PORT}`);
  console.log(`✓ API proxy connected to ${API_URL}`);
});
