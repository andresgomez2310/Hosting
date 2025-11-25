from flask import Flask, jsonify
from flask_cors import CORS
from templates_routes import templates_bp
from auth_routes import auth_blueprint
from projects_routes import proyectos_blueprint
import os

app = Flask(__name__)
CORS(app)

# Registra los blueprints
app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(proyectos_blueprint, url_prefix="/projects")
app.register_blueprint(templates_bp)

@app.get("/")
def home():
    return {"message": "Hosting Manager API running"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "message": "Manager funcionando correctamente"
    }

# Nuevo endpoint para obtener los templates
@app.route('/api/templates', methods=['GET'])
def get_templates():
    # Obtén la lista de templates (en tu caso desde los directorios)
    templates = []
    template_dirs = ['flask', 'static_template', 'template_react']

    for template in template_dirs:
        template_info = {
            "name": template,
            "description": f"Template {template} description",  # Añade una descripción relevante
            "url": f"/templates/{template}",  # Este será el link para cada template
        }
        templates.append(template_info)

    return jsonify({"templates": templates})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)