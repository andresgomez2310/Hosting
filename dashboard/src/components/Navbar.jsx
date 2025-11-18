import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <div style={{ background: "#222", color: "white", padding: "10px" }}>
      <b>Panel de Control</b> &nbsp; | &nbsp;
      <Link style={{ color: "white" }} to="/dashboard">Inicio</Link>
    </div>
  );
}
