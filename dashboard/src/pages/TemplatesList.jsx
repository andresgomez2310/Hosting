import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles.css"; // Asegúrate de que el CSS tenga los estilos adecuados

export default function TemplatesList() {
  const [templates, setTemplates] = useState([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTemplates = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        alert("Necesitas iniciar sesión.");
        navigate("/login");
        return;
      }

      try {
        const response = await fetch("http://localhost:5000/api/templates", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Error al obtener los templates.");
        }

        const data = await response.json();
        setTemplates(data.templates); // Asumiendo que la respuesta contiene un arreglo de templates
      } catch (error) {
        setError("Hubo un problema al obtener los templates.");
        console.error("Error fetching templates:", error);
      }
    };

    fetchTemplates();
  }, [navigate]);

  // Función para copiar el código
  const copyCode = (code) => {
    navigator.clipboard.writeText(code);
    alert("¡Código copiado al portapapeles!");
  };

  return (
    <div className="card">
      <h1 className="title">Templates Disponibles</h1>

      {error && <p className="error-text">{error}</p>}

      {templates.length === 0 ? (
        <p>No hay templates disponibles.</p>
      ) : (
        <div className="templates-container">
          {templates.map((template, index) => (
            <div key={index} className="template-card">
              <h3>{template.name}</h3>
              <p>{template.description}</p>

              {/* Mostrar el código de cada template */}
              <div className="template-content">
                <h4>Archivos necesarios:</h4>
                <pre className="code-snippet">{template.code}</pre> {/* Aquí usamos el campo 'code' que contiene el código del template */}
                <button 
                  className="btn-small copy-btn"
                  onClick={() => copyCode(template.code)}
                >
                  Copiar código
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <button
        className="btn-small back-btn"
        onClick={() => navigate("/projects")}
      >
        ← Volver a Mis Proyectos
      </button>
    </div>
  );
}
