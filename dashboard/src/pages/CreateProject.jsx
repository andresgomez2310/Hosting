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
      // 🔥 createProject SOLO recibe estos dos parámetros
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