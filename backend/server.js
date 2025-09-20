const express = require('express');
const app = express();
const PORT = process.env.PORT || 4000;

// Middleware for JSON
app.use(express.json());

// Simple health check route
app.get('/api/ping', (req, res) => {
  res.json({ message: 'Bridge Backend is alive ⚓' });
});

// Example placeholder route for future expansion
app.get('/api/status', (req, res) => {
  res.json({ status: 'operational', timestamp: Date.now() });
});

// Start server
app.listen(PORT, () => {
  console.log(`Backend running at http://localhost:${PORT}`);
});
