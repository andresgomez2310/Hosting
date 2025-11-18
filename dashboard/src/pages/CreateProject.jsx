import React, { useState } from "react";
import { createProject } from "../api";
import { useNavigate } from "react-router-dom";

export default function CreateProject() {
    const [name, setName] = useState("");
    const navigate = useNavigate();

    const handleCreate = async () => {
        const token = localStorage.getItem("token");
        const res = await createProject(token, { name });

        if (res.success) {
            alert("Proyecto creado");
            navigate("/projects");
        } else {
            alert("Error: " + res.message);
        }
    };

    return (
        <div className="container">
            <h1>Crear Proyecto</h1>

            <input placeholder="Nombre del proyecto" onChange={e => setName(e.target.value)} />
            <button onClick={handleCreate}>Crear</button>

            <p><a href="/dashboard">Volver</a></p>
        </div>
    );
}
