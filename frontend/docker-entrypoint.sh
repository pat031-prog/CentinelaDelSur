#!/bin/sh

# Fail on error
set -e

# Create runtime config file from environment variables
echo "window.ENV = {" > /usr/share/nginx/html/env-config.js
echo "  API_URL: \"${VITE_API_URL}\"" >> /usr/share/nginx/html/env-config.js
echo "};" >> /usr/share/nginx/html/env-config.js

# Start nginx
exec "$@"
