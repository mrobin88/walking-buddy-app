const http = require('http');

// Test routes
const routes = [
  '/',
  '/chat',
  '/admin',
  '/api/status',
  '/api/admin/stats',
  '/api/admin/users'
];

async function testRoute(route) {
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: 3000,
      path: route,
      method: 'GET'
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        resolve({
          route,
          status: res.statusCode,
          contentType: res.headers['content-type'],
          data: data.substring(0, 100) + (data.length > 100 ? '...' : '')
        });
      });
    });

    req.on('error', (err) => {
      resolve({
        route,
        status: 'ERROR',
        error: err.message
      });
    });

    req.end();
  });
}

async function testAllRoutes() {
  console.log('Testing all routes...\n');
  
  for (const route of routes) {
    const result = await testRoute(route);
    console.log(`Route: ${route}`);
    console.log(`Status: ${result.status}`);
    if (result.contentType) {
      console.log(`Content-Type: ${result.contentType}`);
    }
    if (result.data) {
      console.log(`Data: ${result.data}`);
    }
    if (result.error) {
      console.log(`Error: ${result.error}`);
    }
    console.log('---');
  }
}

testAllRoutes(); 