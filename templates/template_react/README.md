# Template React

Este es un template base de React diseñado para la plataforma de hosting basada en contenedores.  
El objetivo es permitir que los usuarios desplieguen proyectos React dentro de su propio contenedor Docker.

---

## 🧱 Características

- React 18 con estructura limpia
- Diseño simple y moderno listo para personalizar
- Dockerfile optimizado para producción
- Servido con **Nginx**

---

## 🗂 Estructura del proyecto

template_react/
├── Dockerfile
├── package.json
├── package-lock.json
├── public/
│ ├── index.html
│ └── favicon.ico
└── src/
├── App.js
├── App.css
├── index.js
└── index.css

## Cómo ejecutar el template con Docker

### 1. Construir la imagen

docker build -t react-template .

### 2. Ejecutar el contenedor
docker run -d -p 8080:80 react-template

### 3. Acceder desde el navegador
http://localhost:8080
