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
    } catch (err) {
      setError("Error de red.");
    }
  };

  return (
    <div className="card">
      <h1>Crear cuenta</h1>

      <form onSubmit={handleRegister}>
        <input placeholder="Nombre completo" value={name} onChange={(e) => setName(e.target.value)} />
        <input placeholder="Correo" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input type="password" placeholder="Contraseña" value={password} onChange={(e) => setPassword(e.target.value)} />

        {error && <p style={{ color: "red" }}>{error}</p>}
        <button className="btn" type="submit">Registrarse</button>
      </form>

      <Link to="/login" className="btn-small">Volver</Link>
    </div>
  );
}
