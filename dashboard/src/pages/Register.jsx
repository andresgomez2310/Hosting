import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { registerUser } from "../api";
import "../styles.css";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await registerUser({ name, email, password });
      if (res.success) {
        alert("Registro exitoso. Ahora inicia sesión.");
        navigate("/login");
      } else {
        setError(res.error || "No se pudo registrar.");
      }
    } catch {
      setError("Error de red.");
    }
  };

  return (
    <div className="center-screen">
      <div className="dashboard-hero-card login-hero-card">

        <h1 className="hero-title">Hosting Platform</h1>
        <p className="hero-subtitle">Tu base digital para el éxito en línea</p>

        <h2 className="login-title">Crear cuenta</h2>

        <form onSubmit={handleRegister} className="login-form">
          <input 
            type="text"
            placeholder="Nombre completo" 
            value={name} 
            onChange={(e) => setName(e.target.value)} 
            required
          />

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

          {error && <p style={{ color: "red" }}>{error}</p>}

          <button className="btn" type="submit">Registrarse</button>
        </form>

        <Link to="/login" className="btn-back">← Volver</Link>

      </div>
    </div>
  );
}
