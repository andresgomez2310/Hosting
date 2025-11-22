const API_URL = "";

export async function login(email, password) {
  const r = await fetch(`/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  return r.json();
}

export async function registerUser(data) {
  const r = await fetch(`/auth/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return r.json();
}

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

export async function createProject(nombre, repo_url) {
  const token = localStorage.getItem("token");

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

export async function getMyProjects() {
  const token = localStorage.getItem("token");

  const r = await fetch(`/projects/mine`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return r.json();
}
