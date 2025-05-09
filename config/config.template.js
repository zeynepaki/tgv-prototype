const TYPESENSE_CLIENT_CONFIG = {
    nodes: [{
        host: '${TYPESENSE_HOST}',
        port: '${TYPESENSE_PORT}',
        protocol: '${TYPESENSE_PROTOCOL}',
        path: '${TYPESENSE_PATH}',
    }],
    apiKey: '${TYPESENSE_API_KEY}',
    connectionTimeoutSeconds: 2
};
