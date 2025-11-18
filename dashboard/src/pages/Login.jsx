import React, { useState } from "react";
import { login, sendTokenToMonitor } from "../api";
import { useNavigate } from "react-router-dom";

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    const handleLogin = async () => {
        const res = await login(email, password);

        if (!res.success) {
            alert("Credenciales incorrectas");
            return;
        }

        localStorage.setItem("token", res.accessToken);

        // activar monitor del backend
        await sendTokenToMonitor(res.accessToken);

        navigate("/dashboard");
    };

    return (
        <div className="container">
            <h1>Iniciar Sesión</h1>

            <input type="email" placeholder="Correo" onChange={e => setEmail(e.target.value)} />
            <input type="password" placeholder="Contraseña" onChange={e => setPassword(e.target.value)} />

            <button onClick={handleLogin}>Entrar</button>

            <p>¿No tienes cuenta? <a href="/register">Regístrate</a></p>
        </div>
    );
}
