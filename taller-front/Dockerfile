# Etapa 1: Construcción de la aplicación Angular
FROM node:18 AS build

WORKDIR /app

COPY package*.json ./
RUN npm install -g @angular/cli@19.2.1
RUN npm install

COPY . .

RUN ng build --configuration production

# Etapa 2: Servir la aplicación con NGINX
FROM nginx:alpine

COPY --from=build /app/dist/taller-front /usr/share/nginx/html

# Configuración de NGINX para manejar la subruta /taller
RUN sed -i 's|location / {|location /taller/ { alias /usr/share/nginx/html/; }|' /etc/nginx/conf.d/default.conf

EXPOSE 80
