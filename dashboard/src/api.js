const API_URL = "";

// ===============================
// 🔐 LOGIN
// ===============================
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
    // Guardamos el token
    localStorage.setItem("token", res.accessToken);

    // Guardamos el user_id para asociar proyectos
    if (res.user && res.user._id) {
      localStorage.setItem("user_id", res.user._id);
    }
  }

  return res;
}

// ===============================
// 🧑‍💻 REGISTRO
// ===============================
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

// ===============================
// 📡 ENVIAR TOKEN AL MONITOR
// ===============================
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

// ===============================
// 📁 CREAR PROYECTO
// ===============================
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

// ===============================
// 📂 OBTENER MIS PROYECTOS
// ===============================

export async function getMyProjects() {
  try {
    const res = await fetch(`/projects/mine`);   // 👈 usa la ruta RELATIVA

    return await res.json();
  } catch (err) {
    console.error("API error:", err);
    return { error: "No se pudo conectar con el servidor." };
  }
}


// ===============================
// 🛠️ ACTUALIZAR TABLA
// ===============================
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


// ===============================
// 🗑️ ELIMINAR PROYECTO
// ===============================
export async function deleteProject(id) {
  const token = localStorage.getItem("token");

  if (!token) {
    return { error: "Sin token" };
  }

  const r = await fetch(`/projects/delete/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  return r.json();
}


