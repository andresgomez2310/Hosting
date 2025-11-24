const API_URL = ""; // Asegúrate de tener la URL base correcta aquí si es necesario

// Función para hacer login
export async function login(email, password) {
  const r = await fetch(`/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const res = await r.json();
  
  if (res.success) {
    // Guardamos el token en el localStorage
    localStorage.setItem("token", res.accessToken);
  }

  return res;
}

// Función para registrar un nuevo usuario
export async function registerUser(data) {
  const r = await fetch(`/auth/signup-direct`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return r.json();
}

// Función para enviar el token al monitor
export async function sendTokenToMonitor(token) {
  const r = await fetch(`/auth/use_token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ accessToken: token }),
  });

  return r.json();
}

// Función para crear un proyecto
export async function createProject(nombre, repo_url) {
  const token = localStorage.getItem("token");

  if (!token) {
    throw new Error("No token found in localStorage");
  }

  const r = await fetch(`/projects/create`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ nombre, repo_url }),
  });

  return r.json();
}

// Función para obtener los proyectos del usuario
export async function getMyProjects() {
  const token = localStorage.getItem("token");

  if (!token) {
    throw new Error("No token found in localStorage");
  }

  const r = await fetch(`/projects/mine`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return r.json();
}

// Función para actualizar una tabla existente
export async function updateTable(tableName, description, columns) {
  const token = localStorage.getItem("token");

  if (!token) {
    throw new Error("No token found in localStorage");
  }

  const r = await fetch(`/database/pc2_394e10a6d2/update-table/${tableName}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      tableName: tableName,
      description: description,
      columns: columns
    }),
  });

  return r.json();
}
