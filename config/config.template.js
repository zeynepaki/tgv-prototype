const TYPESENSE_CLIENT_CONFIG = {
    nodes: [{
      host: 'localhost',
      port: '80',
      protocol: 'http',
      path: '/api',
    }],
    apiKey: '${TYPESENSE_API_KEY}',
    connectionTimeoutSeconds: 2
  };