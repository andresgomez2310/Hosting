// api.js – versión final CORRECTA

export async function login(email, password) {
    const res = await fetch(`/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });
    return res.json();
}

export async function registerUser(data) {
    const res = await fetch(`/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return res.json();
}

// Necesario para activar el monitor del backend
export async function sendTokenToMonitor(accessToken) {
    return fetch(`/auth/use_token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ accessToken })
    }).then(res => res.json());
}

export async function getProjects(token) {
    const res = await fetch(`/projects/mine`, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });
    return res.json();
}

export async function createProject(token, data) {
    const res = await fetch(`/projects/create`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(data)
    });
    return res.json();
}
