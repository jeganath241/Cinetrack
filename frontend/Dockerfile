# Frontend stage
FROM node:18-alpine as frontend

WORKDIR /app/frontend

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install -g vite
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Expose ports
EXPOSE 3000

# Run the application
CMD ["npm", "run", "dev"]
