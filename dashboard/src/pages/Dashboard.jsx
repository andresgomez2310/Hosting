import React from "react";
import { Link } from "react-router-dom";
import "../styles.css";

export default function Dashboard() {
  return (
    <div className="center-screen">
      <div className="dashboard-hero-card">

        <h1 className="hero-title">Hosting Platform</h1>
        <p className="hero-subtitle">Tu base digital para el éxito en línea</p>

        {/* Botón Mis Proyectos */}
        <Link to="/projects" className="dashboard-primary-btn">
          <span className="dash-icon">📁</span>
          Mis proyectos
        </Link>

        {/* Botón Crear Proyecto (nuevo estilo) */}
        <Link to="/projects/create" className="dashboard-secondary-btn">
          Crear proyecto
        </Link>

      </div>
    </div>
  );
}
