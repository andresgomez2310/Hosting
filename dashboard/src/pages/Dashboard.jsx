import React from "react";
import { Link } from "react-router-dom";
import "../styles.css";

export default function Dashboard() {
  return (
    <div className="card dashboard">
      <h1 className="title">Panel Principal</h1>

      <div className="dashboard-buttons">
        <Link className="btn dashboard-btn" to="/projects">
          Mis proyectos
        </Link>

        <Link className="btn dashboard-btn" to="/projects/create">
          Crear proyecto
        </Link>
      </div>
    </div>
  );
}
