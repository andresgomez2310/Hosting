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
    setError(""); // Limpiar cualquier error anterior

    console.group("%c🔵 LOGIN FLOW", "color: #2563eb");

    console.log("→ Intentando iniciar sesión…");
    console.log("Email usado:", email);

    try {
      // Llamar a la función de login (desde api.js)
      const res = await login(email, password);

      console.log("Respuesta del backend:", res);

      if (res.success) {
        console.log("✔ Login exitoso");
        console.log("AccessToken recibido:", res.accessToken);

        // Guardar el token en localStorage
        localStorage.setItem("token", res.accessToken);

        console.log("→ Enviando token al monitor…");
        const monitorResponse = await sendTokenToMonitor(res.accessToken); // Enviar el token al monitor
        console.log("Monitor respondió:", monitorResponse);

        console.log("✔ Redirigiendo al Dashboard…");
        navigate("/dashboard"); // Redirigir al Dashboard
      } else {
        console.warn("❌ Login fallido:", res.message);
        setError(res.message || "Credenciales inválidas");
      }
    } catch (err) {
      console.error("⚠ Error de red:", err);
      setError("Error de red al intentar iniciar sesión.");
    }

    console.groupEnd();
  };

  return (
    <div className="card">
      <h1>Iniciar sesión</h1>

      <form onSubmit={handleSubmit}>
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
  );
}
