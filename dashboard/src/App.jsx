import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import ProjectList from "./pages/ProjectList.jsx";
import CreateProject from "./pages/CreateProject.jsx";

export default function App() {

    const ProtectedRoute = ({ children }) => {
        const token = localStorage.getItem("token");
        return token ? children : <Navigate to="/login" />;
    };

    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Navigate to="/login" />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                <Route path="/projects" element={<ProtectedRoute><ProjectList /></ProtectedRoute>} />
                <Route path="/create" element={<ProtectedRoute><CreateProject /></ProtectedRoute>} />
            </Routes>
        </BrowserRouter>
    );
}
