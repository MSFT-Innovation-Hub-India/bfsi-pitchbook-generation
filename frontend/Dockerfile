# Build React app
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --legacy-peer-deps && \
    chmod -R +x node_modules/.bin
COPY . .
RUN npm run build

# Serve with Node
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/build ./build
COPY startup.sh .
RUN chmod +x startup.sh
EXPOSE 8080
CMD ["./startup.sh"]
