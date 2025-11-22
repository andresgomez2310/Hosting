import './App.css';

export default function App() {
  return (
    <div className="container">
      <div className="card">
        <h1>React Template</h1>
        <p>
          Este es el template React para la plataforma de hosting basada en contenedores. 
          Puedes modificarlo a tu gusto y desplegarlo dentro de un contenedor Docker.
        </p>

        <a href="#" className="btn">
          Ver documentación
        </a>
      </div>

      <footer>
        © {new Date().getFullYear()} Template React — Docker
      </footer>
    </div>
  );
}
