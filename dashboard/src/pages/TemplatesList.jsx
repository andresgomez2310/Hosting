import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles.css";

import hljs from "highlight.js/lib/common";
import "highlight.js/styles/github-dark.css";

export default function TemplatesList() {
  const [templates, setTemplates] = useState([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const ICONS = {
    "Aplicación Flask": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg",
    "Sitio Web Estático": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg",
    "Aplicación React": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg"
  };

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Necesitas iniciar sesión.");
      navigate("/login");
      return;
    }

    fetch("/api/templates", {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
      .then((res) => res.json())
      .then((data) => {
        setTemplates(data.templates || []);
      })
      .catch(() => setError("Error al cargar los templates"));
  }, [navigate]);

  const copyCode = (content, filename) => {
    navigator.clipboard.writeText(content);
    alert(`Contenido de ${filename} copiado`);
  };

  const downloadZip = (folderName) => {
    window.location.href = `/api/templates/${folderName}/download`;
  };

  /** ⭐ EJECUTA HIGHLIGHT CUANDO SE ABRE UN <details> */
  const handleToggle = (e) => {
    if (e.target.open) {
      const blocks = e.target.querySelectorAll("pre code");
      blocks.forEach((block) => {
        hljs.highlightElement(block);
      });
    }
  };

  return (
    <div className="templates-page">
      <h1 className="templates-title">📦 Templates Disponibles</h1>

      {error && <p className="error-text">{error}</p>}

      <div className="templates-container">
        {templates.map((template, index) => (
          <div key={index} className="template-card">

            {/* HEADER */}
            <div className="template-header">
              <img src={ICONS[template.name]} className="template-icon" />
              <h2>{template.name}</h2>

              <button
                className="download-btn"
                onClick={() => downloadZip(template.folder)}
              >
                📥 Descargar ZIP
              </button>
            </div>

            {/* LISTA DE ARCHIVOS */}
            <h4>Archivos del template:</h4>

            {Object.keys(template.files).map((filename, idx) => (
              <details
                key={idx}
                className="file-details animated"
                onToggle={handleToggle}
              >
                <summary className="file-summary">{filename}</summary>

                <pre className="code-snippet">
                  <code
                    dangerouslySetInnerHTML={{
                      __html: hljs.highlightAuto(template.files[filename]).value
                    }}
                  ></code>
                </pre>

                <button
                  className="copy-btn"
                  onClick={() => copyCode(template.files[filename], filename)}
                >
                  Copiar {filename}
                </button>
              </details>
            ))}
          </div>
        ))}
      </div>

      <button className="btn-small back-btn" onClick={() => navigate("/projects")}>
        ← Volver a Mis Proyectos
      </button>
    </div>
  );
}
