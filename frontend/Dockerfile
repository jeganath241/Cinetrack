
# Frontend stage
FROM node:18-alpine

WORKDIR /app/frontend

# Set npm configuration
# RUN npm config set registry https://registry.npmjs.org/ \
#     && npm config set strict-ssl false \
#     && npm config set legacy-peer-deps true

# Copy package files
COPY frontend/package*.json ./

# Clean install dependencies
# RUN rm -rf node_modules package-lock.json
# RUN npm cache clean --force

# Install dependencies and Vite globally
RUN npm install -g vite
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Expose ports
EXPOSE 3000

# Run the application
# CMD ["sh", "-c", "cd /app/backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]
CMD ["npm", "run", "dev"]
