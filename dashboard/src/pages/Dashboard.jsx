import React from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Dashboard() {
    const navigate = useNavigate();

    const logout = () => {
        localStorage.removeItem("token");
        navigate("/login");
    };

    return (
        <div className="container">
            <h1>Panel Principal</h1>

            <nav>
                <Link to="/projects">Mis Proyectos</Link><br/>
                <Link to="/create">Crear Proyecto</Link><br/><br/>

                <button 
                    onClick={logout} 
                    style={{
                        marginTop: "10px",
                        background: "red",
                        color: "white",
                        padding: "8px 12px",
                        border: "none",
                        borderRadius: "6px",
                        cursor: "pointer"
                    }}
                >
                    Cerrar Sesión
                </button>
            </nav>
        </div>
    );
}
