const API = location.port === "5500" ? "http://127.0.0.1:8000" : "/api";

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

let token = localStorage.getItem("fs_token"); 

// Small helper's 
function toast(msg, ok = false) {
  const t = $("#toast");
  t.textContent = msg;
  t.className = "show" + (ok ? " ok" : "");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => (t.className = ""), 3500);
}

// One function for every API call: adds the token and turns errors into readable messages
async function api(path, { method = "GET", json, form } = {}) {
  const headers = {};
  let body;
  if (token) headers.Authorization = "Bearer " + token;
  if (json) { headers["Content-Type"] = "application/json"; body = JSON.stringify(json); }
  if (form) body = new URLSearchParams(form);   // login must be sent as form data

  let res;
  try { res = await fetch(API + path, { method, headers, body }); }
  catch { throw new Error("Cannot reach the server. Is FastAPI running on port 8000?"); }

  const data = await res.json().catch(() => ({}));
  if (res.status === 401 && token && path !== "/auth/login") { logout(); throw new Error("Session expired. Please log in again."); }
  if (!res.ok) {
    const d = data.detail;
    throw new Error(Array.isArray(d) ? d.map((e) => e.loc.slice(1).join(".") + ": " + e.msg).join("; ") : d || "Request failed");
  }
  return data;
}

// Run an async action while disabling the submit button
async function withButton(btn, fn) {
  btn.disabled = true;
  try { await fn(); } catch (e) { toast(e.message); } finally { btn.disabled = false; }
} 

// Login / register
$$(".tab").forEach((tab) => tab.addEventListener("click", () => {
  $$(".tab").forEach((t) => t.classList.toggle("active", t === tab));
  $("#loginForm").hidden = tab.dataset.tab !== "login";
  $("#registerForm").hidden = tab.dataset.tab !== "register";
}));

async function login(username, password) {
  const data = await api("/auth/login", { method: "POST", form: { username, password } });
  token = data.access_token;
  localStorage.setItem("fs_token", token);
  await startApp();
}

$("#loginForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  withButton($("button", e.target), () => login(f.get("username"), f.get("password")));
});

$("#registerForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const f = Object.fromEntries(new FormData(e.target));
  withButton($("button", e.target), async () => {
    await api("/auth/register", { method: "POST", json: f });
    await login(f.username, f.password);          // log in right after registering
  });
});

function logout() {
  token = null;
  localStorage.removeItem("fs_token");
  $("#app").hidden = true;
  $("#auth").hidden = false;
}
$("#logoutBtn").addEventListener("click", logout);

async function startApp() {
  const me = await api("/users/me");
  $("#userName").textContent = me.username;
  $("#userMail").textContent = me.email;
  $("#avatar").textContent = me.username[0].toUpperCase();
  $("#auth").hidden = true;
  $("#app").hidden = false;
  go("dashboard");
}

// Navigation 
const TITLES = { dashboard: "Dashboard", risk: "Loan Repayment Risk", segment: "Customer Segmentation", chat: "Financial Assistant" };

function go(view) {
  $$(".view").forEach((v) => (v.hidden = v.id !== "view-" + view));
  $$(".nav").forEach((n) => n.classList.toggle("active", n.dataset.view === view));
  $("#pageTitle").textContent = TITLES[view];
  $("#sidebar").classList.remove("open");
  if (view === "dashboard") loadDashboard();
}
$$(".nav").forEach((n) => n.addEventListener("click", () => go(n.dataset.view)));
$$("[data-go]").forEach((c) => c.addEventListener("click", () => go(c.dataset.go)));
$("#menuBtn").addEventListener("click", () => $("#sidebar").classList.toggle("open"));

// Dashboard 
const ICONS = { "ml/predict": "📉", "ml/segment": "👥", "rag/chat": "💬" };

async function loadDashboard() {
  try {
    const logs = await api("/logs?limit=200");
    const count = (ep) => logs.filter((l) => l.endpoint === ep).length;
    $("#stats").innerHTML = [
      ["Total requests", logs.length], ["Assistant chats", count("rag/chat")],
      ["Risk checks", count("ml/predict")], ["Segments found", count("ml/segment")],
    ].map(([label, n]) => `<div class="stat">${label}<b>${n}</b></div>`).join("");

    $("#activity").innerHTML = logs.length
      ? logs.slice(0, 6).map((l) => `<div class="row"><span class="ic">${ICONS[l.endpoint] || "•"}</span>
          <div><b>${esc(l.endpoint)}</b><small>${esc(l.output_text)}</small></div>
          <small>${new Date(l.created_at + "Z").toLocaleString()}</small></div>`).join("")
      : '<p class="muted">No activity yet. Try one of the features!</p>';
  } catch (e) { toast(e.message); }
}

// Dynamic forms 
// [feature name sent to the API, label, sample value, optional?]
const RISK_FIELDS = [
  ["RevolvingUtilizationOfUnsecuredLines", "Credit utilization", 0.766],
  ["age", "Age", 45],
  ["NumberOfTime30-59DaysPastDueNotWorse", "Times 30-59 days late", 2],
  ["DebtRatio", "Debt ratio", 0.803],
  ["MonthlyIncome", "Monthly income (optional)", 9120, true],
  ["NumberOfOpenCreditLinesAndLoans", "Open credit lines & loans", 13],
  ["NumberOfTimes90DaysLate", "Times 90+ days late", 0],
  ["NumberRealEstateLoansOrLines", "Real-estate loans", 6],
  ["NumberOfTime60-89DaysPastDueNotWorse", "Times 60-89 days late", 0],
  ["NumberOfDependents", "Dependents (optional)", 2, true],
];
const SEG_FIELDS = [
  ["BALANCE", "Balance", 2100], ["BALANCE_FREQUENCY", "Balance update frequency (0-1)", 1],
  ["PURCHASES", "Total purchases", 3400], ["ONEOFF_PURCHASES", "One-off purchases", 2000],
  ["INSTALLMENTS_PURCHASES", "Installment purchases", 1400], ["CASH_ADVANCE", "Cash advance", 0],
  ["PURCHASES_FREQUENCY", "Purchase frequency (0-1)", 1], ["ONEOFF_PURCHASES_FREQUENCY", "One-off frequency (0-1)", 0.8],
  ["PURCHASES_INSTALLMENTS_FREQUENCY", "Installment frequency (0-1)", 0.7], ["CASH_ADVANCE_FREQUENCY", "Cash-advance frequency (0-1)", 0],
  ["CASH_ADVANCE_TRX", "Cash-advance transactions", 0], ["PURCHASES_TRX", "Purchase transactions", 45],
  ["CREDIT_LIMIT", "Credit limit (optional)", 7500, true], ["PAYMENTS", "Payments", 3300],
  ["MINIMUM_PAYMENTS", "Minimum payments (optional)", 600, true], ["PRC_FULL_PAYMENT", "Share paid in full (0-1)", 0],
  ["TENURE", "Tenure (months)", 12],
];

function buildFields(el, fields) {
  el.innerHTML = fields.map(([name, label, sample, optional]) =>
    `<label>${label}<input type="number" step="any" name="${name}" value="${sample}" ${optional ? "" : "required"}></label>`).join("");
}
buildFields($("#riskFields"), RISK_FIELDS);
buildFields($("#segFields"), SEG_FIELDS);

// Read the form into {name: number}; empty optional fields are left out so the backend uses its defaults
function readFeatures(form) {
  const features = {};
  $$("input", form).forEach((i) => { if (i.value !== "") features[i.name] = parseFloat(i.value); });
  return { features };
}


// Loan risk 
$("#riskForm").addEventListener("submit", (e) => {
  e.preventDefault();
  withButton($("button", e.target), async () => {
    const r = await api("/ml/predict", { method: "POST", json: readFeatures(e.target) });
    const pct = (r.probability * 100).toFixed(1);
    const high = r.prediction === 1;
    $("#riskResult").innerHTML = `
      <h3>Estimated risk</h3>
      <div class="big" style="color:${high ? "var(--plum)" : "#6d8f43"}">${pct}%</div>
      <div class="bar"><i style="width:${pct}%;background:${high ? "var(--plum)" : "var(--green)"}"></i></div>
      <span class="badge ${high ? "high" : "low"}">${high ? "Higher risk: review recommended" : "Lower risk"}</span>
      <p class="note">This is a risk estimate to support human review. It is not an automatic loan decision.</p>`;
  });
}); 

// Segmentation 
$("#segForm").addEventListener("submit", (e) => {
  e.preventDefault();
  withButton($("button", e.target), async () => {
    const r = await api("/ml/segment", { method: "POST", json: readFeatures(e.target) });
    $("#segResult").innerHTML = `
      <div class="seg-icon">${esc(r.icon)}</div>
      <h3>${esc(r.name)}</h3>
      <p class="muted">${esc(r.description)}</p>
      <span class="badge high" style="background:var(--navy)">Cluster ${r.cluster_id}</span>`;
  });
});

// RAG assistant 
const box = $("#messages");

function addMsg(who, text) {
  const m = document.createElement("div");
  m.className = "msg " + who;
  const b = document.createElement("div");
  b.className = "bubble";
  b.textContent = text;                          // textContent keeps model output safe
  m.append(b);
  box.append(m);
  box.scrollTop = box.scrollHeight;
  return m;
}

async function ask(question) {
  addMsg("user", question);
  const wait = addMsg("bot", "");
  wait.firstChild.innerHTML = '<div class="typing"><i></i><i></i><i></i></div>';
  try {
    const r = await api("/rag/chat", { method: "POST", json: { question } });
    wait.firstChild.textContent = r.answer;

    const src = document.createElement("div");   // source chips
    src.className = "sources";
    [...new Set(r.sources)].forEach((s) => { const c = document.createElement("span"); c.textContent = "📄 " + s; src.append(c); });

    const fb = document.createElement("div");    // thumbs up / down -> /feedback
    fb.className = "fb";
    [["👍", 5], ["👎", 1]].forEach(([icon, rating]) => {
      const b = document.createElement("button");
      b.textContent = icon;
      b.onclick = async () => {
        try {
          await api("/feedback", { method: "POST", json: { rating, log_id: r.log_id } });
          $$("button", fb).forEach((x) => (x.disabled = true));
          toast("Thanks for your feedback!", true);
        } catch (err) { toast(err.message); }
      };
      fb.append(b);
    });
    wait.append(src, fb);
  } catch (e) {
    wait.firstChild.textContent = "Sorry, something went wrong: " + e.message;
  }
  box.scrollTop = box.scrollHeight;
}

$("#chatForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const input = $("#chatInput");
  const q = input.value.trim();
  if (!q) return;
  input.value = "";
  ask(q);
});
$$("#chips button").forEach((b) => b.addEventListener("click", () => ask(b.textContent)));

// Start 
if (token) startApp().catch(logout); // already logged in? skip the login screen



