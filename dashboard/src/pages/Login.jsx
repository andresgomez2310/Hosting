import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login, sendTokenToMonitor } from "../api";
import "../styles.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await login(email, password);

      if (res.success) {
        localStorage.setItem("token", res.accessToken);
        await sendTokenToMonitor(res.accessToken);
        navigate("/dashboard");
      } else {
        setError(res.message || "Credenciales inválidas");
      }
    } catch (err) {
      setError("Error de red al intentar iniciar sesión.");
    }
  };

  return (
    <div className="center-screen">
      <div className="dashboard-hero-card login-hero-card">

        <h1 className="hero-title">Hosting Platform</h1>
        <p className="hero-subtitle">Tu base digital para el éxito en línea</p>

        <h2 className="login-title">Iniciar sesión</h2>

        <form onSubmit={handleSubmit} className="login-form">
          <input
            type="email"
            placeholder="Correo electrónico"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && <p style={{ color: "red", marginTop: "10px" }}>{error}</p>}

          <button className="btn" type="submit">Entrar</button>
        </form>

        <p style={{ marginTop: "20px" }}>
          ¿No tienes cuenta? <Link to="/register">Regístrate</Link>
        </p>

      </div>
    </div>
  );
}
