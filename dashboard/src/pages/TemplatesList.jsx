import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "../styles.css";

import hljs from "highlight.js/lib/common";
import "highlight.js/styles/github-dark.css";

export default function TemplatesList() {
  const [templates, setTemplates] = useState([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  // NUEVO: estado para iframe/modal
  const [mountedTemplate, setMountedTemplate] = useState(null); // folder string or null
  const [iframeKey, setIframeKey] = useState(0); // for reload
  const [iframeLoaded, setIframeLoaded] = useState(false);
  const [iframeError, setIframeError] = useState(false);
  const loadTimerRef = useRef(null);

  const ICONS = {
    "Aplicación Flask":
      "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg",
    "Sitio Web Estático":
      "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg",
    "Aplicación React":
      "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg",
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
        Authorization: `Bearer ${token}`,
      },
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

  const handleToggle = (e) => {
    if (e.target.open) {
      const blocks = e.target.querySelectorAll("pre code");
      blocks.forEach((block) => {
        hljs.highlightElement(block);
      });
    }
  };

  // NUEVAS funciones para montar/desmontar
  const openMount = (folder) => {
    setMountedTemplate(folder);
    setIframeKey((k) => k + 1);
    setIframeLoaded(false);
    setIframeError(false);
    // start timeout: if iframe doesn't fire onLoad in 8s, mark error (offer open in new tab)
    if (loadTimerRef.current) {
      clearTimeout(loadTimerRef.current);
    }
    loadTimerRef.current = setTimeout(() => {
      setIframeError(true);
    }, 8000);
  };

  const closeMount = () => {
    setMountedTemplate(null);
    setIframeLoaded(false);
    setIframeError(false);
    if (loadTimerRef.current) {
      clearTimeout(loadTimerRef.current);
    }
  };

  const onIframeLoad = () => {
    setIframeLoaded(true);
    setIframeError(false);
    if (loadTimerRef.current) {
      clearTimeout(loadTimerRef.current);
    }
  };

  // Mapeo de carpetas a repositorios (ajusta patterns si tus folder names son distintos)
  const getRepoUrl = (folder) => {
    if (!folder) return "";
    const f = folder.toLowerCase();
    if (f.includes("react")) return "https://github.com/Znake-G/react_template.git";
    if (f.includes("flask")) return "https://github.com/Znake-G/flask-template.git";
    // fallback para estático/html
    return "https://github.com/Znake-G/static-template.git";
  };

  return (
    <div className="templates-page">
      <h1 className="templates-title">📦 Templates Disponibles</h1>

      {error && <p className="error-text">{error}</p>}

      <div className="templates-container">
        {templates.map((template, index) => (
          <div key={index} className="template-card" data-template={template.folder}>
            {/* HEADER */}
            <div className="template-header">
              <img src={ICONS[template.name]} className="template-icon" />
              <h2>{template.name}</h2>

              {/* ACCIONES: ahora columna (botones apilados) */}
              <div style={{ display: "flex", flexDirection: "column", gap: 8, marginLeft: 12 }}>
                <button className="download-btn" onClick={() => downloadZip(template.folder)}>
                  📥 Descargar ZIP
                </button>

                <button
                  className="download-btn"
                  onClick={() => openMount(template.folder)}
                  title={`Montar ${template.name}`}
                  aria-label={`Montar ${template.name}`}
                >
                  🔎 Montar
                </button>

                {/* NUEVO: vista previa sin levantar containers */}
                <button
                  className="download-btn"
                  onClick={() => window.open(`/preview/${encodeURIComponent(template.folder)}/`, "_blank")}
                  title={`Vista previa ${template.name}`}
                >
                  👁️ Vista previa
                </button>

                {/* NUEVO: enlace al repositorio del template */}
                {template.folder && (
                  <div style={{ marginTop: 6, fontSize: 13 }}>
                    <span style={{ color: "#666" }}>Repo:</span>{" "}
                    <a
                      href={getRepoUrl(template.folder)}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ wordBreak: "break-all" }}
                    >
                      {getRepoUrl(template.folder)}
                    </a>
                  </div>
                )}
              </div>
            </div>

            {/* LISTA DE ARCHIVOS */}
            <h4>Archivos del template:</h4>

            {Object.keys(template.files).map((filename, idx) => (
              <details key={idx} className="file-details animated" onToggle={handleToggle}>
                <summary className="file-summary">{filename}</summary>

                <pre className="code-snippet">
                  <code>{template.files[filename]}</code>
                </pre>

                <button className="copy-btn" onClick={() => copyCode(template.files[filename], filename)}>
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

      {/* MODAL/IFRAME: aparece cuando mountedTemplate !== null */}
      {mountedTemplate && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1200,
          }}
          onClick={closeMount}
        >
          <div
            role="dialog"
            aria-modal="true"
            style={{
              width: "95%",
              height: "90%",
              background: "#fff",
              borderRadius: 8,
              overflow: "hidden",
              position: "relative",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", alignItems: "center", padding: "8px 12px", background: "#111", color: "#fff" }}>
              <strong style={{ marginRight: 12 }}>{mountedTemplate}</strong>

              <button
                onClick={() => {
                  setIframeKey((k) => k + 1);
                  setIframeLoaded(false);
                  setIframeError(false);
                  if (loadTimerRef.current) clearTimeout(loadTimerRef.current);
                  loadTimerRef.current = setTimeout(() => setIframeError(true), 8000);
                }}
                style={{ marginRight: 8 }}
              >
                ↻ Recargar
              </button>

              <button onClick={closeMount} style={{ marginLeft: "auto" }}>
                Cerrar ✕
              </button>
            </div>

            {/* AREA DE IFRAME */}
            <div style={{ width: "100%", height: "calc(100% - 44px)", position: "relative", background: "#f5f7fb" }}>
              {!iframeLoaded && !iframeError && (
                <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", zIndex: 10 }}>
                  <div style={{ padding: 12, background: "#fff", borderRadius: 8, boxShadow: "0 2px 8px rgba(0,0,0,0.2)" }}>
                    Cargando vista del template...
                  </div>
                </div>
              )}

              {iframeError && (
                <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", zIndex: 10 }}>
                  <div style={{ padding: 12, background: "#fff", borderRadius: 8, boxShadow: "0 2px 8px rgba(0,0,0,0.2)" }}>
                    No se pudo cargar el template en el iframe.
                    <div style={{ marginTop: 8 }}>
                      <a href={`/templates/${encodeURIComponent(mountedTemplate)}/`} target="_blank" rel="noopener noreferrer">
                        Abrir en nueva pestaña
                      </a>
                    </div>
                  </div>
                </div>
              )}

              <iframe
                key={iframeKey}
                src={`/templates/${encodeURIComponent(mountedTemplate)}/`}
                title={`mounted-${mountedTemplate}`}
                onLoad={onIframeLoad}
                style={{ width: "100%", height: "100%", border: 0 }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
