# Stage 1: Build React frontend
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Build React application
RUN npm run build


# Stage 2: Run Express server
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies
RUN npm install --omit=dev

# Copy server file
COPY server.js .

# Copy React build files
COPY --from=build /app/dist ./dist

# Cloud Run uses the PORT environment variable
ENV NODE_ENV=production

EXPOSE 8080

# Start Express server
CMD ["node", "server.js"]
