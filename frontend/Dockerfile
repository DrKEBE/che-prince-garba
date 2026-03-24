# Étape de build : compilation avec Vite
FROM node:18-alpine AS builder

WORKDIR /app

# Copier les fichiers de dépendances
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --only=production

# Copier le code source et construire
COPY frontend/ .
RUN npm run build:prod

# Étape finale : servir avec Nginx
FROM nginx:alpine

# Copier les fichiers statiques
COPY --from=builder /app/dist /usr/share/nginx/html

# Copier la configuration Nginx personnalisée (optionnelle)
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]