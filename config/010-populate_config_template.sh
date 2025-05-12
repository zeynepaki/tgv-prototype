# Interpolate environment variables:
#   ... in the web front end:
envsubst < /usr/share/nginx/html/config.template.js > /usr/share/nginx/html/config.js
#   ... and in the nginx configuration:
envsubst '$TYPESENSE_UPSTREAM_HOST' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf
