import React, { useEffect, useState } from "react";
import { getProjects } from "../api";
import { Link } from "react-router-dom";

export default function ProjectList() {
    const [projects, setProjects] = useState([]);

    useEffect(() => {
        const token = localStorage.getItem("token");

        getProjects(token).then(res => {
            if (res.success) {
                setProjects(res.projects || []);
            } else {
                console.error(res);
            }
        });
    }, []);

    return (
        <div className="container">
            <h1>Mis Proyectos</h1>

            <ul>
                {projects.map(p => (
                    <li key={p.id}>{p.name}</li>
                ))}
            </ul>

            <Link to="/dashboard">Volver</Link>
        </div>
    );
}
