import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className={`sidebar ${collapsed ? "collapsed" : ""}`}>
      
      {/* BOTÓN DE COLAPSAR */}
      <button className="collapse-btn" onClick={() => setCollapsed(!collapsed)}>
        {collapsed ? "→" : "←"}
      </button>

      {/* LINKS */}
      <div className="sidebar-links">
        <Link className="sidebar-item" to="/dashboard">
          <span className="icon">🏠</span>
          {!collapsed && <span className="label">Inicio</span>}
        </Link>

        <Link className="sidebar-item" to="/projects">
          <span className="icon">📁</span>
          {!collapsed && <span className="label">Mis proyectos</span>}
        </Link>

        <Link className="sidebar-item" to="/projects/create">
          <span className="icon">➕</span>
          {!collapsed && <span className="label">Crear proyecto</span>}
        </Link>
      </div>

      {/* LOGOUT */}
      <button className="sidebar-logout" onClick={logout}>
        <span className="icon">🚪</span>
        {!collapsed && <span className="label">Cerrar sesión</span>}
      </button>

    </div>
  );
}
