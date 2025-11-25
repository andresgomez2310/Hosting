import { BrowserRouter, Routes, Route } from "react-router-dom";

// Pages
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import ProjectList from "./pages/ProjectList.jsx";
import CreateProject from "./pages/CreateProject.jsx";
import TemplatesList from "./pages/TemplatesList.jsx";
// Components
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Layout from "./components/Layout.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* === PUBLIC ROUTES (SIN SIDEBAR) === */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* === RUTA INICIAL (DESPUÉS DE LOGIN) === */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        

        {/* === DASHBOARD === */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* === PROJECT LIST === */}
        <Route
          path="/projects"
          element={
            <ProtectedRoute>
              <Layout>
                <ProjectList />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* === CREATE PROJECT === */}
        <Route
          path="/projects/create"
          element={
            <ProtectedRoute>
              <Layout>
                <CreateProject />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* === TEMPLATES LIST === */}
        <Route
          path="/templates"
          element={
            <ProtectedRoute>
              <Layout>
                <TemplatesList />
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
