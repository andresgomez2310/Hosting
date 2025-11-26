import React, { useEffect, useState } from "react";
import { getMyProjects } from "../api";
import { useNavigate, Link } from "react-router-dom";
import "../styles.css";

export default function ProjectList() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Necesitas iniciar sesión.");
      navigate("/login");
      return;
    }

    const load = async () => {
      try {
        const res = await getMyProjects();

        if (res.error) {
          setError(res.error);
          return;
        }

        if (!Array.isArray(res.projects)) {
          setError("No se pudieron cargar los proyectos.");
          return;
        }

        setProjects(res.projects);
      } catch (err) {
        console.error("Error al cargar proyectos:", err);
        setError("Error de red.");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [navigate]);

  const openProject = (p) => {
    if (!p.host) return alert("Este proyecto no tiene host todavía.");
    window.open(`http://${p.host}`, "_blank");
  };

  const deleteProject = (p) => {
    const ok = confirm(`¿Eliminar proyecto "${p.name}"?`);
    if (!ok) return;

    // Aquí iría tu delete real si lo implementas:
    // await deleteProjectAPI(p._id)

    setProjects(projects.filter((x) => x._id !== p._id));
  };

  if (loading) return <p>Cargando proyectos…</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div className="templates-page">
      <h1 className="templates-title">🗂️ Mis Proyectos</h1>

      {projects.length === 0 ? (
        <div className="empty-box" style={{ textAlign: "center" }}>
          No tienes proyectos creados todavía.
          <br /><br />
          <Link to="/projects/create" className="btn-small">
            💡 Crear un nuevo proyecto
          </Link>
        </div>
      ) : (
        <div className="templates-container">
          {projects.map((p) => (
            <ProjectCard
              key={p._id}
              project={p}
              onOpen={openProject}
              onDelete={deleteProject}
            />
          ))}
        </div>
      )}
    </div>
  );
}

/* ==========================================================
   TARJETA DEL PROYECTO (igual estilo que las plantillas)
   ========================================================== */

function ProjectCard({ project, onOpen, onDelete }) {
  return (
    <div className="template-card project-card">

      {/* ENCABEZADO */}
      <div className="template-header">
        <h2 className="project-title">🚀 {project.name}</h2>

        <span
          className="project-status"
          style={{
            background: project.status === "created" ? "green" : "gray",
            padding: "6px 12px",
            borderRadius: "8px",
            color: "white",
            fontWeight: "600",
          }}
        >
          {project.status}
        </span>
      </div>

      {/* INFO */}
      <div className="project-info">
        <p><strong>🔗 Repositorio:</strong> {project.rep_url}</p>
        <p><strong>🌐 Host:</strong> {project.host}</p>
        <p><strong>📦 Contenedor:</strong> {project.container_id || "No asignado"}</p>

        <p style={{ marginTop: "10px" }}>
          🕒 <strong>Creado:</strong> {new Date(project.created_at).toLocaleString()}
        </p>

        <p>
          🔄 <strong>Último acceso:</strong> {new Date(project.last_access).toLocaleString()}
        </p>
      </div>

      {/* BOTONES */}
      <div className="project-actions">
        <button className="project-btn" onClick={() => onOpen(project)}>
          🌍 Abrir
        </button>

        <button
          className="project-btn project-btn-danger"
          onClick={() => onDelete(project)}
        >
          🗑️ Eliminar
        </button>
      </div>
    </div>
  );
}
