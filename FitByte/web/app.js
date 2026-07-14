function getAccessToken() {
    return localStorage.getItem("accessToken");
}

function getRefreshToken() {
    return localStorage.getItem("refreshToken");
}

function requireAuth() {
    if (!getAccessToken()) {
        window.location.href = "/web/login.html";
    }
}

function setUserEmail() {
    const emailElement = document.querySelector("[data-user-email]");
    if (emailElement) {
        emailElement.textContent = localStorage.getItem("userEmail") || "Signed in";
    }
}

function logout() {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("userEmail");
    window.location.href = "/web/login.html";
}

async function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        throw new Error("Missing refresh token");
    }

    const response = await fetch("/api/refresh", {
        method: "POST",
        headers: {
            Authorization: `Bearer ${refreshToken}`,
        },
    });

    if (!response.ok) {
        throw new Error("Unable to refresh access token");
    }

    const data = await response.json();
    localStorage.setItem("accessToken", data.token);
    return data.token;
}

async function apiFetch(path, options = {}) {
    const headers = {
        ...(options.headers || {}),
        Authorization: `Bearer ${getAccessToken()}`,
    };

    if (options.body && !headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
    }

    let response = await fetch(path, {
        ...options,
        headers,
    });

    if (response.status === 401 && getRefreshToken()) {
        try {
            const newAccessToken = await refreshAccessToken();
            response = await fetch(path, {
                ...options,
                headers: {
                    ...headers,
                    Authorization: `Bearer ${newAccessToken}`,
                },
            });
        } catch (error) {
            logout();
            throw error;
        }
    }

    return response;
}

function toISOFromDateTimeLocal(value) {
    return new Date(value).toISOString();
}

function formatDateTime(value) {
    return new Date(value).toLocaleString([], {
        dateStyle: "medium",
        timeStyle: "short",
    });
}

function newestByDate(items, fieldName) {
    return [...items].sort((a, b) => new Date(b[fieldName]) - new Date(a[fieldName]))[0];
}

function escapeHTML(value) {
    const element = document.createElement("div");
    element.textContent = value;
    return element.innerHTML;
}

function setupShell() {
    requireAuth();
    setUserEmail();

    const logoutButton = document.querySelector("[data-logout]");
    if (logoutButton) {
        logoutButton.addEventListener("click", logout);
    }
}
