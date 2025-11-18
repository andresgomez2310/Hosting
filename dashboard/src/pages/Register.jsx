import React, { useState } from "react";
import { registerUser } from "../api";
import { useNavigate } from "react-router-dom";

export default function Register() {
    const [data, setData] = useState({
        email: "",
        password: "",
        name: ""
    });

    const navigate = useNavigate();

    const handleRegister = async () => {
        const res = await registerUser(data);
        alert(res.message);

        if (res.success) navigate("/login");
    };

    return (
        <div className="container">
            <h1>Registro</h1>

            <input placeholder="Nombre" onChange={e => setData({ ...data, name: e.target.value })} />
            <input type="email" placeholder="Correo" onChange={e => setData({ ...data, email: e.target.value })} />
            <input type="password" placeholder="Contraseña" onChange={e => setData({ ...data, password: e.target.value })} />

            <button onClick={handleRegister}>Crear cuenta</button>

            <p>¿Ya tienes cuenta? <a href="/login">Inicia sesión</a></p>
        </div>
    );
}
