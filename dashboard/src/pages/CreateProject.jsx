import React, { useState } from "react";
import { createProject } from "../api";
import { useNavigate } from "react-router-dom";
import "../styles.css";

export default function CreateProject() {
  const [name, setName] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleCreate = async () => {
    setError("");

    const token = localStorage.getItem("token");
    if (!token) {
      alert("Necesitas iniciar sesión.");
      navigate("/login");
      return;
    }

    // Validaciones simples
    if (!name.trim()) {
      setError("Debes ingresar un nombre de proyecto.");
      return;
    }

    if (!repoUrl.trim() || !repoUrl.startsWith("https://")) {
      setError("Debes ingresar un repositorio válido de GitHub.");
      return;
    }

    try {
      const res = await createProject(name, repoUrl);

      if (res?.success) {
        alert("Proyecto creado correctamente");
        navigate("/projects");
      } else {
        setError(res?.message || "No se pudo crear el proyecto.");
      }
    } catch (err) {
      console.error("Error al crear proyecto:", err);
      setError("Error de red al crear el proyecto.");
    }
  };

  return (
    <div className="card create-card">
      <h1 className="title">Crear Proyecto</h1>

      <div className="form-group">
        <label>Nombre del Proyecto</label>
        <input
          placeholder="mi-sitio-web"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>URL del Repositorio GitHub</label>
        <input
          placeholder="https://github.com/usuario/repositorio"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
        />
        <small>El repositorio debe contener un Dockerfile</small>
      </div>

      {/* =======================================================
          🔥 BLOQUE A LA FUERZA — NO DEPENDE DE TU CSS
          SI ESTO NO SE VE ► tu layout NO está renderizando este componente
      ========================================================== */}
      <div style={{
        marginTop: "25px",
        padding: "15px",
        borderRadius: "10px",
        border: "3px solid red",
        background: "#fff7cc",
        color: "#000",
        textAlign: "left"
      }}>
        <h3 style={{ marginBottom: "10px" }}>
          📦 ¿No tienes un repositorio aún?
        </h3>

        <p style={{ marginBottom: "8px", fontWeight: "bold" }}>
          Templates disponibles:
        </p>

        {/* Enlace a los templates dinámicamente */}
        <a
          href="/templates"  // Ahora redirige a /templates, que es el enlace de la lista de templates.
          target="_blank"
          style={{
            display: "inline-block",
            color: "#2563eb",
            marginBottom: "10px",
            fontWeight: "bold"
          }}
        >
          → Ver templates listos
        </a>

        <p style={{ fontSize: "14px", color: "#444" }}>
          Incluyen Dockerfile + estructura base para desplegar rápido.
        </p>
      </div>

      {/* ======================================================= */}

      {error && <p className="error-text">{error}</p>}

      <button className="btn" onClick={handleCreate}>
        Crear
      </button>

      <button
        className="btn-small back-btn"
        onClick={() => navigate("/projects")}
      >
        ← Volver a Mis Proyectos
      </button>
    </div>
  );
}
