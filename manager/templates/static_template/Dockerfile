# ========================================
# Template estático: HTML + CSS + JS
# ========================================

FROM nginx:1.25-alpine

WORKDIR /usr/share/nginx/html

# Copiar todos los archivos del template
COPY . .

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
