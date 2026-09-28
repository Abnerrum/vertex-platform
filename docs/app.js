const SAME_ORIGIN_API =
  (window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost") &&
  window.location.port === "8000";

const API_BASE = SAME_ORIGIN_API
  ? "/api/v1"
  : "http://127.0.0.1:8000/api/v1";

const state = {
  token: localStorage.getItem("vertex_token") || "",
  user: null,
  clients: [],
  projects: [],
  serviceOrders: []
};

const titles = {
  dashboard: "Visão geral",
  clientes: "Clientes",
  projetos: "Projetos",
  servicos: "Serviços / OS",
  roadmap: "Roadmap"
};

const statusLabel = {
  active: "Ativo",
  inactive: "Inativo",
  planning: "Planejamento",
  development: "Desenvolvimento",
  testing: "Testes",
  completed: "Concluído",
  open: "Aberta",
  assigned: "Atribuída",
  in_progress: "Em andamento",
  waiting: "Aguardando",
  cancelled: "Cancelada"
};

const priorityLabel = {
  low: "Baixa",
  medium: "Média",
  high: "Alta",
  urgent: "Urgente"
};

function $(id) {
  return document.getElementById(id);
}

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;

  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch (_) {
    const error = new Error(
      window.location.hostname.includes("netlify")
        ? "O site do Netlify está sem backend. Para a demo funcional, abra http://127.0.0.1:8000/app/"
        : "Não foi possível conectar à API. Confirme se o backend está rodando."
    );
    error.status = 0;
    throw error;
  }

  if (response.status === 204) return null;

  let data = {};
  try {
    data = await response.json();
  } catch (_) {}

  if (!response.ok) {
    const detail = typeof data.detail === "string" ? data.detail : "Não foi possível concluir a operação.";
    const error = new Error(detail);
    error.status = response.status;
    throw error;
  }

  return data;
}

function showToast(message, type = "success") {
  const toast = $("toast");
  toast.textContent = message;
  toast.className = `toast ${type}`;
  setTimeout(() => toast.className = "toast hidden", 3200);
}

function setLoginMessage(message, type = "error") {
  const el = $("loginMessage");
  el.textContent = message;
  el.className = `message ${type}`;
}

function setAuthenticated(authData) {
  state.token = authData.access_token;
  state.user = authData.user;
  localStorage.setItem("vertex_token", state.token);
  openApp();
}

function logout() {
  state.token = "";
  state.user = null;
  localStorage.removeItem("vertex_token");
  $("appShell").classList.add("hidden");
  $("loginScreen").classList.remove("hidden");
}

function initials(name = "Usuário") {
  return name.split(" ").filter(Boolean).slice(0, 2).map(p => p[0]).join("").toUpperCase();
}

function openApp() {
  $("loginScreen").classList.add("hidden");
  $("appShell").classList.remove("hidden");
  if (state.user) {
    $("userName").textContent = state.user.name;
    $("userInitials").textContent = initials(state.user.name);
  }
  loadAll();
}

async function restoreSession() {
  if (!state.token) return;
  try {
    state.user = await api("/auth/me");
    openApp();
  } catch (_) {
    logout();
  }
}

$("loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  setLoginMessage("Entrando...", "info");

  try {
    const result = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: $("loginEmail").value.trim(),
        password: $("loginPassword").value
      })
    });
    setLoginMessage("");
    setAuthenticated(result);
  } catch (error) {
    setLoginMessage(error.message);
  }
});

$("bootstrapForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  setLoginMessage("Criando administrador...", "info");

  try {
    const result = await api("/auth/bootstrap", {
      method: "POST",
      body: JSON.stringify({
        name: $("bootstrapName").value.trim(),
        email: $("bootstrapEmail").value.trim(),
        password: $("bootstrapPassword").value
      })
    });
    setLoginMessage("");
    showToast("Administrador criado. Você já está conectado.");
    setAuthenticated(result);
  } catch (error) {
    setLoginMessage(error.status === 409 ? "O administrador inicial já existe. Use o login acima." : error.message);
  }
});

document.querySelectorAll("nav button").forEach(btn => btn.addEventListener("click", () => {
  document.querySelectorAll("nav button").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".page").forEach(p => p.classList.remove("show"));
  btn.classList.add("active");
  const id = btn.dataset.page;
  $(id).classList.add("show");
  $("title").textContent = titles[id];
}));

$("logoutBtn").addEventListener("click", logout);
$("refreshBtn").addEventListener("click", loadAll);
$("newClientBtn").addEventListener("click", openClientForm);
$("newProjectBtn").addEventListener("click", openProjectForm);
$("newOsBtn").addEventListener("click", openOsForm);
$("closeModalBtn").addEventListener("click", closeModal);
$("modal").addEventListener("click", (event) => {
  if (event.target.id === "modal") closeModal();
});

async function loadAll() {
  $("apiStatus").textContent = "Atualizando dados...";
  $("apiStatus").className = "api-status";

  try {
    const [dashboard, clients, projects, orders] = await Promise.all([
      api("/dashboard"),
      api("/clients"),
      api("/projects"),
      api("/service-orders")
    ]);

    state.clients = clients;
    state.projects = projects;
    state.serviceOrders = orders;

    renderDashboard(dashboard);
    renderClients();
    renderProjects();
    renderServiceOrders();

    $("apiStatus").textContent = `API online • v${dashboard.version}`;
    $("apiStatus").className = "api-status online";
  } catch (error) {
    $("apiStatus").textContent = "API indisponível";
    $("apiStatus").className = "api-status offline";
    if (error.status === 401) logout();
    else showToast(error.message, "error");
  }
}

function renderDashboard(data) {
  $("totalClients").textContent = data.totals.clients;
  $("totalProjects").textContent = data.totals.projects;
  $("totalOs").textContent = data.totals.service_orders;
  $("totalOpenOs").textContent = data.totals.open_service_orders;

  const active = state.projects.filter(p => !["completed", "cancelled"].includes(p.status)).slice(0, 4);
  $("dashboardProjects").innerHTML = active.length
    ? active.map(p => `
      <div class="project">
        <b>${escapeHtml(p.name)}</b>
        <span>${p.progress}%</span>
        <div><i style="width:${p.progress}%"></i></div>
        <small>${escapeHtml(statusLabel[p.status] || p.status)} • ${escapeHtml(priorityLabel[p.priority] || p.priority)}</small>
      </div>
    `).join("")
    : '<div class="empty-state">Nenhum projeto em andamento.</div>';
}

function renderClients() {
  $("clientsRows").innerHTML = state.clients.length
    ? state.clients.map(c => `
      <div class="row">
        <b>${escapeHtml(c.company_name)}</b>
        <span>${escapeHtml(c.responsible_name)}</span>
        <em>${escapeHtml(statusLabel[c.status] || c.status)}</em>
      </div>
    `).join("")
    : '<div class="empty-state padded">Nenhum cliente cadastrado.</div>';
}

function projectCard(project) {
  const client = state.clients.find(c => c.id === project.client_id);
  return `
    <div class="kanban-card">
      <b>${escapeHtml(project.name)}</b>
      <p>${escapeHtml(client?.company_name || "Cliente")} • ${project.progress}%</p>
      <div class="mini-progress"><i style="width:${project.progress}%"></i></div>
    </div>
  `;
}

function renderProjects() {
  const planning = state.projects.filter(p => p.status === "planning");
  const development = state.projects.filter(p => p.status === "development");
  const testing = state.projects.filter(p => !["planning", "development"].includes(p.status));

  $("projectsPlanning").innerHTML = planning.map(projectCard).join("") || '<div class="empty-state">Vazio</div>';
  $("projectsDevelopment").innerHTML = development.map(projectCard).join("") || '<div class="empty-state">Vazio</div>';
  $("projectsTesting").innerHTML = testing.map(projectCard).join("") || '<div class="empty-state">Vazio</div>';
}

function nextStatus(current) {
  const flow = ["open", "assigned", "in_progress", "waiting", "completed"];
  const index = flow.indexOf(current);
  return index >= 0 && index < flow.length - 1 ? flow[index + 1] : null;
}

function renderServiceOrders() {
  $("osRows").innerHTML = state.serviceOrders.length
    ? state.serviceOrders.map(order => {
        const next = nextStatus(order.status);
        return `
          <div class="row os">
            <button class="link-button" data-history="${order.id}">${escapeHtml(order.code)}</button>
            <span>${escapeHtml(order.title)}</span>
            <strong class="${order.priority === "urgent" || order.priority === "high" ? "high" : ""}">${escapeHtml(priorityLabel[order.priority] || order.priority)}</strong>
            <em>${escapeHtml(statusLabel[order.status] || order.status)}</em>
            <span>${next ? `<button class="small-action" data-advance="${order.id}" data-next="${next}">Avançar</button>` : "Finalizada"}</span>
          </div>
        `;
      }).join("")
    : '<div class="empty-state padded">Nenhuma OS cadastrada.</div>';

  document.querySelectorAll("[data-history]").forEach(btn => btn.addEventListener("click", () => openHistory(btn.dataset.history)));
  document.querySelectorAll("[data-advance]").forEach(btn => btn.addEventListener("click", () => advanceOrder(btn.dataset.advance, btn.dataset.next)));
}

async function advanceOrder(id, next) {
  try {
    await api(`/service-orders/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: next, note: "Atualização realizada pela interface demonstrativa" })
    });
    showToast(`OS atualizada para ${statusLabel[next] || next}.`);
    await loadAll();
  } catch (error) {
    showToast(error.message, "error");
  }
}

function openModal(title, html) {
  $("modalTitle").textContent = title;
  $("modalBody").innerHTML = html;
  $("modal").classList.remove("hidden");
}

function closeModal() {
  $("modal").classList.add("hidden");
  $("modalBody").innerHTML = "";
}

function clientOptions(selected = "") {
  return state.clients.map(c => `<option value="${c.id}" ${String(c.id) === String(selected) ? "selected" : ""}>${escapeHtml(c.company_name)}</option>`).join("");
}

function projectOptions(clientId = null) {
  const projects = clientId ? state.projects.filter(p => p.client_id === Number(clientId)) : state.projects;
  return '<option value="">Sem projeto</option>' + projects.map(p => `<option value="${p.id}">${escapeHtml(p.name)}</option>`).join("");
}

function openClientForm() {
  openModal("Novo cliente", `
    <form id="clientForm" class="form-stack">
      <label>Empresa<input id="clientCompany" required></label>
      <label>Responsável<input id="clientResponsible" required></label>
      <div class="form-grid">
        <label>E-mail<input id="clientEmail" type="email"></label>
        <label>Telefone<input id="clientPhone"></label>
      </div>
      <button class="primary wide" type="submit">Salvar cliente</button>
    </form>
  `);

  $("clientForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await api("/clients", {
        method: "POST",
        body: JSON.stringify({
          company_name: $("clientCompany").value.trim(),
          responsible_name: $("clientResponsible").value.trim(),
          email: $("clientEmail").value.trim() || null,
          phone: $("clientPhone").value.trim() || null
        })
      });
      closeModal();
      showToast("Cliente cadastrado.");
      await loadAll();
    } catch (error) {
      showToast(error.message, "error");
    }
  });
}

function openProjectForm() {
  if (!state.clients.length) {
    showToast("Cadastre um cliente antes de criar um projeto.", "error");
    return;
  }

  openModal("Novo projeto", `
    <form id="projectForm" class="form-stack">
      <label>Cliente<select id="projectClient" required><option value="">Selecione</option>${clientOptions()}</select></label>
      <label>Nome do projeto<input id="projectName" required></label>
      <div class="form-grid">
        <label>Tipo
          <select id="projectType"><option value="web">Sistema Web</option><option value="app">Aplicativo</option><option value="automation">Automação</option><option value="data">Dados / BI</option></select>
        </label>
        <label>Status
          <select id="projectStatus"><option value="planning">Planejamento</option><option value="development">Desenvolvimento</option><option value="testing">Testes</option><option value="completed">Concluído</option></select>
        </label>
      </div>
      <div class="form-grid">
        <label>Prioridade
          <select id="projectPriority"><option value="low">Baixa</option><option value="medium" selected>Média</option><option value="high">Alta</option></select>
        </label>
        <label>Progresso (%)<input id="projectProgress" type="number" min="0" max="100" value="0"></label>
      </div>
      <button class="primary wide" type="submit">Salvar projeto</button>
    </form>
  `);

  $("projectForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await api("/projects", {
        method: "POST",
        body: JSON.stringify({
          client_id: Number($("projectClient").value),
          name: $("projectName").value.trim(),
          project_type: $("projectType").value,
          status: $("projectStatus").value,
          priority: $("projectPriority").value,
          progress: Number($("projectProgress").value || 0)
        })
      });
      closeModal();
      showToast("Projeto cadastrado.");
      await loadAll();
    } catch (error) {
      showToast(error.message, "error");
    }
  });
}

function openOsForm() {
  if (!state.clients.length) {
    showToast("Cadastre um cliente antes de criar uma OS.", "error");
    return;
  }

  openModal("Nova Ordem de Serviço", `
    <form id="osForm" class="form-stack">
      <label>Cliente<select id="osClient" required><option value="">Selecione</option>${clientOptions()}</select></label>
      <label>Projeto<select id="osProject"><option value="">Selecione o cliente primeiro</option></select></label>
      <label>Título<input id="osTitle" required></label>
      <label>Descrição<textarea id="osDescription" rows="3"></textarea></label>
      <div class="form-grid">
        <label>Prioridade
          <select id="osPriority"><option value="low">Baixa</option><option value="medium" selected>Média</option><option value="high">Alta</option><option value="urgent">Urgente</option></select>
        </label>
        <label>Status
          <select id="osStatus"><option value="open">Aberta</option><option value="assigned">Atribuída</option><option value="in_progress">Em andamento</option><option value="waiting">Aguardando</option></select>
        </label>
      </div>
      <label>Prazo<input id="osDueDate" type="date"></label>
      <button class="primary wide" type="submit">Criar OS</button>
    </form>
  `);

  $("osClient").addEventListener("change", () => {
    $("osProject").innerHTML = projectOptions($("osClient").value);
  });

  $("osForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const projectValue = $("osProject").value;
      await api("/service-orders", {
        method: "POST",
        body: JSON.stringify({
          client_id: Number($("osClient").value),
          project_id: projectValue ? Number(projectValue) : null,
          title: $("osTitle").value.trim(),
          description: $("osDescription").value.trim() || null,
          priority: $("osPriority").value,
          status: $("osStatus").value,
          due_date: $("osDueDate").value || null
        })
      });
      closeModal();
      showToast("Ordem de Serviço criada.");
      await loadAll();
    } catch (error) {
      showToast(error.message, "error");
    }
  });
}

async function openHistory(id) {
  try {
    const history = await api(`/service-orders/${id}/history`);
    openModal("Histórico da OS", history.length
      ? `<div class="history-list">${history.map(item => `
          <div class="history-item">
            <b>${escapeHtml(item.field)}</b>
            <span>${escapeHtml(item.old_value ?? "—")} → ${escapeHtml(item.new_value ?? "—")}</span>
            <small>${escapeHtml(item.note || "Alteração registrada")}</small>
          </div>
        `).join("")}</div>`
      : '<div class="empty-state">Nenhum histórico registrado.</div>');
  } catch (error) {
    showToast(error.message, "error");
  }
}

restoreSession();
