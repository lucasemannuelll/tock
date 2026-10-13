// ==========================================================
// Estado global
// ==========================================================
const state = {
    projects: [],
    tags: [],
    entries: [],
    runningEntryId: null,
    timerInterval: null,
    timerStart: null,
};

// ==========================================================
// Helpers
// ==========================================================
async function api(path, options = {}) {
    const res = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`API ${res.status}: ${text}`);
    }
    if (res.status === 204) return null;
    return res.json();
}

function formatDuration(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    const h = String(Math.floor(totalSeconds / 3600)).padStart(2, "0");
    const m = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, "0");
    const s = String(totalSeconds % 60).padStart(2, "0");
    return `${h}:${m}:${s}`;
}

function formatEntryRange(started, ended) {
    const s = new Date(started);
    const e = ended ? new Date(ended) : null;
    const fmt = (d) =>
        d.toLocaleString("pt-BR", { hour12: false });
    return e ? `${fmt(s)} → ${fmt(e)}` : `${fmt(s)} → (em andamento)`;
}

function entryDurationMs(entry) {
    const s = new Date(entry.started_at).getTime();
    const e = entry.ended_at ? new Date(entry.ended_at).getTime() : Date.now();
    return Math.max(0, e - s);
}

// ==========================================================
// Renderização
// ==========================================================
function renderProjects() {
    const select = document.getElementById("project-select");
    const current = select.value;
    select.innerHTML = '<option value="">-- sem projeto --</option>';
    for (const p of state.projects) {
        const opt = document.createElement("option");
        opt.value = String(p.id);
        opt.textContent = p.name;
        select.appendChild(opt);
    }
    select.value = current;

    const list = document.getElementById("projects-list");
    list.innerHTML = "";
    for (const p of state.projects) {
        const li = document.createElement("li");
        li.textContent = `${p.id} - ${p.name} `;
        const btn = document.createElement("button");
        btn.textContent = "Deletar";
        btn.onclick = () => deleteProject(p.id);
        li.appendChild(btn);
        list.appendChild(li);
    }
}

function renderTags() {
    const select = document.getElementById("tags-select");
    const previouslySelected = Array.from(select.selectedOptions).map(
        (o) => o.value
    );
    select.innerHTML = "";
    for (const t of state.tags) {
        const opt = document.createElement("option");
        opt.value = String(t.id);
        opt.textContent = t.name;
        if (previouslySelected.includes(String(t.id))) opt.selected = true;
        select.appendChild(opt);
    }

    const list = document.getElementById("tags-list");
    list.innerHTML = "";
    for (const t of state.tags) {
        const li = document.createElement("li");
        li.textContent = `${t.id} - ${t.name} `;
        const btn = document.createElement("button");
        btn.textContent = "Deletar";
        btn.onclick = () => deleteTag(t.id);
        li.appendChild(btn);
        list.appendChild(li);
    }
}

function renderEntries() {
    const list = document.getElementById("entries-list");
    list.innerHTML = "";
    for (const entry of state.entries) {
        const li = document.createElement("li");

        const project = state.projects.find((p) => p.id === entry.project_id);
        const projectName = project ? project.name : "(sem projeto)";
        const tagNames = entry.tags.map((t) => t.name).join(", ");

        const info = document.createElement("span");
        info.textContent =
            `#${entry.id} [${projectName}] ${entry.description} ` +
            `| ${formatEntryRange(entry.started_at, entry.ended_at)} ` +
            `| duração: ${formatDuration(entryDurationMs(entry))} ` +
            `| tags: ${tagNames || "-"} `;
        li.appendChild(info);

        // Botão parar (se em andamento)
        if (!entry.ended_at) {
            const stopBtn = document.createElement("button");
            stopBtn.textContent = "Parar";
            stopBtn.onclick = () => stopEntryById(entry.id);
            li.appendChild(stopBtn);
        }

        // Botão deletar
        const delBtn = document.createElement("button");
        delBtn.textContent = "Deletar";
        delBtn.onclick = () => deleteEntry(entry.id);
        li.appendChild(delBtn);

        list.appendChild(li);
    }
}

function renderTimerButton() {
    const btn = document.getElementById("start-stop-btn");
    btn.textContent = state.runningEntryId ? "Parar" : "Iniciar";
}

// ==========================================================
// Timer
// ==========================================================
function startTimerLoop() {
    stopTimerLoop();
    state.timerInterval = setInterval(() => {
        if (!state.timerStart) return;
        const elapsed = Date.now() - state.timerStart;
        document.getElementById("elapsed").textContent = formatDuration(elapsed);
        renderEntries(); // atualiza duração dos em andamento
    }, 1000);
}

function stopTimerLoop() {
    if (state.timerInterval) {
        clearInterval(state.timerInterval);
        state.timerInterval = null;
    }
}

function updateElapsedDisplay() {
    if (state.timerStart) {
        document.getElementById("elapsed").textContent = formatDuration(
            Date.now() - state.timerStart
        );
    } else {
        document.getElementById("elapsed").textContent = "00:00:00";
    }
}

// ==========================================================
// Ações - Projects
// ==========================================================
async function loadProjects() {
    state.projects = await api("/api/projects");
    renderProjects();
}

async function createProject() {
    const input = document.getElementById("new-project-name");
    const name = input.value.trim();
    if (!name) return;
    await api("/api/projects", {
        method: "POST",
        body: JSON.stringify({ name }),
    });
    input.value = "";
    await loadProjects();
}

async function deleteProject(id) {
    await api(`/api/projects/${id}`, { method: "DELETE" });
    await loadProjects();
    await loadEntries();
}

// ==========================================================
// Ações - Tags
// ==========================================================
async function loadTags() {
    state.tags = await api("/api/tags");
    renderTags();
}

async function createTag() {
    const input = document.getElementById("new-tag-name");
    const name = input.value.trim();
    if (!name) return;
    await api("/api/tags", {
        method: "POST",
        body: JSON.stringify({ name }),
    });
    input.value = "";
    await loadTags();
}

async function deleteTag(id) {
    await api(`/api/tags/${id}`, { method: "DELETE" });
    await loadTags();
    await loadEntries();
}

// ==========================================================
// Ações - Time Entries
// ==========================================================
async function loadEntries() {
    state.entries = await api("/api/time_entries");
    // detecta entry em andamento
    const running = state.entries.find((e) => !e.ended_at);
    state.runningEntryId = running ? running.id : null;
    state.timerStart = running ? new Date(running.started_at).getTime() : null;
    renderEntries();
    renderTimerButton();
    updateElapsedDisplay();
    if (state.runningEntryId) startTimerLoop();
    else stopTimerLoop();
}

async function startEntry() {
    const projectIdRaw = document.getElementById("project-select").value;
    const projectId = projectIdRaw ? Number(projectIdRaw) : null;
    const description = document.getElementById("description").value.trim() || "(sem descrição)";

    const tagSelect = document.getElementById("tags-select");
    const selectedTagIds = Array.from(tagSelect.selectedOptions).map((o) =>
        Number(o.value)
    );

    const entry = await api("/api/time_entries/start", {
        method: "POST",
        body: JSON.stringify({ project_id: projectId, description }),
    });

    // associa tags selecionadas
    for (const tagId of selectedTagIds) {
        await api(`/api/time_entries/${entry.id}/tags`, {
            method: "POST",
            body: JSON.stringify({ tag_id: tagId }),
        });
    }

    await loadEntries();
}

async function stopEntryById(id) {
    await api(`/api/time_entries/${id}/stop`, { method: "POST" });
    await loadEntries();
}

async function stopCurrentEntry() {
    if (!state.runningEntryId) return;
    await stopEntryById(state.runningEntryId);
}

async function deleteEntry(id) {
    await api(`/api/time_entries/${id}`, { method: "DELETE" });
    await loadEntries();
}

async function toggleStartStop() {
    if (state.runningEntryId) {
        await stopCurrentEntry();
    } else {
        await startEntry();
    }
}

// ==========================================================
// Inicialização
// ==========================================================
async function init() {
    document
        .getElementById("start-stop-btn")
        .addEventListener("click", toggleStartStop);
    document
        .getElementById("create-project-btn")
        .addEventListener("click", createProject);
    document
        .getElementById("create-tag-btn")
        .addEventListener("click", createTag);

    await loadProjects();
    await loadTags();
    await loadEntries();
}

document.addEventListener("DOMContentLoaded", init);
