from flask import Flask
from flask_cors import CORS

from auth_routes import auth_blueprint
from projects_routes import proyectos_blueprint

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(proyectos_blueprint, url_prefix="/projects")

@app.get("/")
def home():
    return {"message": "Hosting Manager API running"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "message": "Manager funcionando correctamente"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
