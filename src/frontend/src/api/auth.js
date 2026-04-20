const API_BASE = `http://${window.location.hostname}:5000`;

export async function registerUser(email, password, confirmPassword) {
    const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
            email,
            password,
            confirmPassword,
        }),
    });

    const data = await res.json();

    if (!res.ok) {
        throw new Error(data.error || "Registration failed");
    }

    return data;
}

export async function loginUser(email, password) {
    const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
            email,
            password,
        }),
    });

    const data = await res.json();

    if (!res.ok) {
        throw new Error(data.error || "Login failed");
    }

    return data;
}

export async function getCurrentUser() {
    const res = await fetch(`${API_BASE}/auth/me`, {
        method: "GET",
        credentials: "include",
    });

    const data = await res.json();
    return data;
}

export async function logoutUser() {
    const res = await fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        credentials: "include",
    });

    const data = await res.json();

    if (!res.ok) {
        throw new Error(data.error || "Logout failed");
    }

    return data;
}
