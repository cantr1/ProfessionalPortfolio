const state = {
  token: localStorage.getItem("yoga_access_token"),
  refreshToken: localStorage.getItem("yoga_refresh_token"),
  sessions: [],
};

const authView = document.querySelector("#auth-view");
const calendarView = document.querySelector("#calendar-view");
const loginForm = document.querySelector("#login-form");
const signupForm = document.querySelector("#signup-form");
const authMessage = document.querySelector("#auth-message");
const calendarMessage = document.querySelector("#calendar-message");
const calendarGrid = document.querySelector("#calendar-grid");
const sessionDialog = document.querySelector("#session-dialog");
const sessionDialogContent = document.querySelector("#session-dialog-content");

document.querySelector("#show-login").addEventListener("click", () => {
  showAuthTab("login");
});

document.querySelector("#show-signup").addEventListener("click", () => {
  showAuthTab("signup");
});

document.querySelector("#logout-button").addEventListener("click", logout);
document.querySelector("#refresh-sessions").addEventListener("click", loadSessions);
loginForm.addEventListener("submit", handleLogin);
signupForm.addEventListener("submit", handleSignup);

if (state.token) {
  showCalendar();
  loadSessions();
}

function showAuthTab(tabName) {
  const loginIsActive = tabName === "login";

  loginForm.classList.toggle("hidden", !loginIsActive);
  signupForm.classList.toggle("hidden", loginIsActive);
  document.querySelector("#show-login").classList.toggle("active", loginIsActive);
  document.querySelector("#show-signup").classList.toggle("active", !loginIsActive);
  setMessage(authMessage, "");
}

async function handleLogin(event) {
  event.preventDefault();
  setMessage(authMessage, "Logging in...");

  const formData = new FormData(loginForm);

  const result = await apiRequest("/api/login", {
    method: "POST",
    body: {
      email: formData.get("email"),
      password: formData.get("password"),
    },
  });

  if (!result.ok) {
    setMessage(authMessage, result.message, true);
    return;
  }

  state.token = result.data.token;
  state.refreshToken = result.data.refresh_token;
  localStorage.setItem("yoga_access_token", state.token);
  localStorage.setItem("yoga_refresh_token", state.refreshToken);

  showCalendar();
  loadSessions();
}

async function handleSignup(event) {
  event.preventDefault();
  setMessage(authMessage, "Creating your account...");

  const formData = new FormData(signupForm);

  const result = await apiRequest("/api/users", {
    method: "POST",
    body: {
      name: formData.get("name"),
      email: formData.get("email"),
      password: formData.get("password"),
    },
  });

  if (!result.ok) {
    setMessage(authMessage, result.message, true);
    return;
  }

  setMessage(authMessage, "Account created. Try logging in now.");
  signupForm.reset();
  showAuthTab("login");
}

async function loadSessions() {
  setMessage(calendarMessage, "Loading sessions...");

  const result = await apiRequest("/api/sessions", {
    method: "GET",
    token: state.token,
  });

  if (!result.ok) {
    setMessage(calendarMessage, result.message, true);
    return;
  }

  state.sessions = result.data ?? [];
  renderCalendar(state.sessions);
  setMessage(calendarMessage, `${state.sessions.length} sessions loaded.`);
}

function renderCalendar(sessions) {
  calendarGrid.innerHTML = "";

  const days = buildNextSevenDays();
  const sessionsByDay = groupSessionsByDay(sessions);

  for (const day of days) {
    const column = document.createElement("section");
    column.className = "day-column";

    const heading = document.createElement("h3");
    heading.className = "day-heading";
    heading.textContent = formatDayHeading(day);
    column.append(heading);

    const sessionsForDay = sessionsByDay.get(toDateKey(day)) ?? [];

    if (sessionsForDay.length === 0) {
      const empty = document.createElement("p");
      empty.className = "empty-day";
      empty.textContent = "No classes";
      column.append(empty);
    }

    for (const session of sessionsForDay) {
      column.append(createSessionCard(session));
    }

    calendarGrid.append(column);
  }
}

function createSessionCard(session) {
  const button = document.createElement("button");
  button.className = "session-card";
  button.type = "button";

  button.innerHTML = `
    <strong>${escapeHTML(session.description)}</strong>
    <span>${formatTimeRange(session.start_time, session.end_time)}</span>
    <span>Instructor: ${session.instructor_name ?? shortID(session.instructor_id)}</span>
    <span>Difficulty: ${session.difficulty}</span>
  `;

  button.addEventListener("click", () => openSessionDialog(session));
  return button;
}

function openSessionDialog(session) {
  sessionDialogContent.innerHTML = `
    <p class="eyebrow">Reserve Class</p>
    <h3>${escapeHTML(session.description)}</h3>
    <p>${formatFullDate(session.start_time)}</p>
    <p>${formatTimeRange(session.start_time, session.end_time)}</p>
    <p>Difficulty: ${session.difficulty}/5</p>
    <p>Class size: ${session.class_size}</p>
    <div class="session-actions">
      <button id="register-session" type="button">Register</button>
      <button id="cancel-dialog" class="secondary-button" type="button">Cancel</button>
    </div>
    <p id="dialog-message" class="form-message" aria-live="polite"></p>
  `;

  document.querySelector("#cancel-dialog").addEventListener("click", () => {
    sessionDialog.close();
  });

  document.querySelector("#register-session").addEventListener("click", () => {
    registerForSession(session.id);
  });

  sessionDialog.showModal();
}

async function registerForSession(sessionID) {
  const dialogMessage = document.querySelector("#dialog-message");
  setMessage(dialogMessage, "Reserving your spot...");

  const result = await apiRequest(`/api/sessions/${sessionID}/registrations`, {
    method: "POST",
    token: state.token,
  });

  if (!result.ok) {
    setMessage(dialogMessage, result.message, true);
    return;
  }

  setMessage(dialogMessage, "You are registered.");

  // CHALLENGE: after registering, show a visual checkmark on the session card.
  // Think about where that state should live: in `state.sessions`, or separately?
}

function showCalendar() {
  authView.classList.add("hidden");
  calendarView.classList.remove("hidden");
}

function logout() {
  state.token = "";
  state.refreshToken = "";
  state.sessions = [];
  localStorage.removeItem("yoga_access_token");
  localStorage.removeItem("yoga_refresh_token");
  calendarView.classList.add("hidden");
  authView.classList.remove("hidden");
  loginForm.reset();
  signupForm.reset();
}

async function apiRequest(path, options = {}) {
  const headers = new Headers();
  headers.set("Accept", "application/json");

  if (options.body) {
    headers.set("Content-Type", "application/json");
  }

  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }

  try {
    const response = await fetch(path, {
      method: options.method ?? "GET",
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    const contentType = response.headers.get("content-type") ?? "";
    const data = contentType.includes("application/json")
      ? await response.json()
      : null;

    if (!response.ok) {
      return {
        ok: false,
        status: response.status,
        message: data?.error ?? `${response.status} ${response.statusText}`,
      };
    }

    return { ok: true, status: response.status, data };
  } catch (error) {
    return {
      ok: false,
      status: 0,
      message: `Network error: ${error.message}`,
    };
  }
}

function buildNextSevenDays() {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  return Array.from({ length: 7 }, (_, index) => {
    const day = new Date(today);
    day.setDate(today.getDate() + index);
    return day;
  });
}

function groupSessionsByDay(sessions) {
  const map = new Map();

  for (const session of sessions) {
    const key = toDateKey(new Date(session.start_time));
    const list = map.get(key) ?? [];
    list.push(session);
    list.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
    map.set(key, list);
  }

  return map;
}

function toDateKey(date) {
  return date.toISOString().slice(0, 10);
}

function formatDayHeading(date) {
  return new Intl.DateTimeFormat(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
  }).format(date);
}

function formatFullDate(value) {
  return new Intl.DateTimeFormat(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
  }).format(new Date(value));
}

function formatTimeRange(start, end) {
  const formatter = new Intl.DateTimeFormat(undefined, {
    hour: "numeric",
    minute: "2-digit",
  });

  return `${formatter.format(new Date(start))} - ${formatter.format(new Date(end))}`;
}

function shortID(id) {
  return id ? `${id.slice(0, 8)}...` : "unknown";
}

function escapeHTML(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setMessage(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle("error", isError);
}
