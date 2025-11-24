import React, { useEffect, useState } from "react";
import { getMyProjects } from "../api";
import { useNavigate, Link } from "react-router-dom";

export default function ProjectList() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
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
        setError("Error de red al cargar proyectos.");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [navigate]);

  if (loading) return <p>Cargando proyectos…</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div className="card">
      <h1>Mis proyectos</h1>

      {projects.length === 0 ? (
        <div className="empty-box">
          No tienes proyectos creados todavía.
          <br /><br />
          <Link to="/projects/create" className="btn-small">
            💡 Tip: ¿Quieres crear uno nuevo?
          </Link>
        </div>
      ) : (
        <ul>
          {projects.map((p) => (
            <li key={p._id}>{p.name}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
