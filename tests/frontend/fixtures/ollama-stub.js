const http = require('http');

const PORT = 11434;

const server = http.createServer((req, res) => {
  // Add CORS headers as needed
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');

  if (req.method === 'GET' && req.url === '/api/tags') {
    res.writeHead(200);
    res.end(JSON.stringify({
      models: [
        { name: "llama3:latest" },
        { name: "mistral:latest" }
      ]
    }));
    return;
  }

  if (req.method === 'POST' && req.url === '/api/generate') {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });
    req.on('end', () => {
      res.writeHead(200);
      res.end(JSON.stringify({
        model: "llama3:latest",
        created_at: new Date().toISOString(),
        response: '{"confidence": 0.9, "category": "project", "reasons": ["Mocked response"]}',
        done: true
      }));
    });
    return;
  }

  res.writeHead(404);
  res.end(JSON.stringify({ error: "Not found" }));
});

server.listen(PORT, () => {
  console.log(`Ollama stub server running on port ${PORT}`);
});
