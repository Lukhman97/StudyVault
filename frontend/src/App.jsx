import { useEffect, useMemo, useState } from "react";
import axios from "axios";

const DEFAULT_API = "http://127.0.0.1:8000/api";

const tabs = [
  { id: "library", label: "Library" },
  { id: "upload", label: "Studio" },
  { id: "admin", label: "Command" }
];

function App() {
  const [apiBase, setApiBase] = useState(localStorage.getItem("sv_api") || DEFAULT_API);
  const [token, setToken] = useState(localStorage.getItem("sv_access") || "");
  const [user, setUser] = useState(localStorage.getItem("sv_user") || "");
  const [isAdmin, setIsAdmin] = useState(localStorage.getItem("sv_admin") === "true");
  const [authMode, setAuthMode] = useState("login");
  const [activeTab, setActiveTab] = useState("library");
  const [status, setStatus] = useState("");

  const [authForm, setAuthForm] = useState({ username: "", email: "", password: "" });
  const [library, setLibrary] = useState({ pdfs: [], roadmaps: [], interviews: [] });
  const [pending, setPending] = useState({ pdfs: [], roadmaps: [], interviews: [] });

  const [pdfUpload, setPdfUpload] = useState({ title: "", file: null, image: null });
  const [roadmapUpload, setRoadmapUpload] = useState({ title: "", description: "", image: null });
  const [interviewUpload, setInterviewUpload] = useState({ company: "", role: "", file: null });

  const api = useMemo(() => apiBase.replace(/\/$/, ""), [apiBase]);

  const http = useMemo(
    () =>
      axios.create({
        baseURL: api,
        timeout: 20000
      }),
    [api]
  );

  const counts = useMemo(
    () => ({
      total: library.pdfs.length + library.roadmaps.length + library.interviews.length,
      pending: pending.pdfs.length + pending.roadmaps.length + pending.interviews.length
    }),
    [library, pending]
  );

  useEffect(() => {
    localStorage.setItem("sv_api", api);
  }, [api]);

  useEffect(() => {
    if (!token) return;
    loadLibrary();
  }, [token]);

  useEffect(() => {
    if (!token || !isAdmin || activeTab !== "admin") return;
    loadPending();
  }, [token, isAdmin, activeTab]);

  async function request(path, options = {}) {
    const { method = "GET", body, auth = false, isForm = false } = options;

    try {
      const response = await http.request({
        url: path,
        method,
        data: body,
        headers: {
          ...(auth ? { Authorization: `Bearer ${token}` } : {}),
          ...(body && !isForm ? { "Content-Type": "application/json" } : {})
        }
      });

      return response.data;
    } catch (error) {
      const message =
        error?.response?.data?.error ||
        error?.response?.data?.detail ||
        error?.message ||
        "Request failed";
      throw new Error(message);
    }
  }

  async function handleAuthSubmit(e) {
    e.preventDefault();
    setStatus("Working...");

    try {
      if (authMode === "signup") {
        await request("/signup/", {
          method: "POST",
          body: {
            username: authForm.username,
            email: authForm.email,
            password: authForm.password
          }
        });
        setStatus("Signup successful. Please login.");
        setAuthMode("login");
        return;
      }

      const data = await request("/login/", {
        method: "POST",
        body: { username: authForm.username, password: authForm.password }
      });

      setToken(data.access);
      setUser(data.username);
      setIsAdmin(Boolean(data.is_admin));

      localStorage.setItem("sv_access", data.access);
      localStorage.setItem("sv_user", data.username || "");
      localStorage.setItem("sv_admin", String(Boolean(data.is_admin)));

      setStatus("Login successful.");
      setAuthForm({ username: "", email: "", password: "" });
    } catch (err) {
      setStatus(err.message);
    }
  }

  function logout() {
    setToken("");
    setUser("");
    setIsAdmin(false);
    setLibrary({ pdfs: [], roadmaps: [], interviews: [] });
    setPending({ pdfs: [], roadmaps: [], interviews: [] });
    localStorage.removeItem("sv_access");
    localStorage.removeItem("sv_user");
    localStorage.removeItem("sv_admin");
    setStatus("Logged out.");
  }

  async function loadLibrary() {
    try {
      const [pdfs, roadmaps, interviews] = await Promise.all([
        request("/pdfs/", { auth: true }),
        request("/roadmaps/", { auth: true }),
        request("/interviews/", { auth: true })
      ]);
      setLibrary({
        pdfs: Array.isArray(pdfs) ? pdfs : [],
        roadmaps: Array.isArray(roadmaps) ? roadmaps : [],
        interviews: Array.isArray(interviews) ? interviews : []
      });
    } catch (err) {
      setStatus(err.message);
    }
  }

  async function loadPending() {
    try {
      const [pdfs, roadmaps, interviews] = await Promise.all([
        request("/admin/pdfs/", { auth: true }),
        request("/admin/roadmaps/", { auth: true }),
        request("/admin/interviews/", { auth: true })
      ]);
      setPending({
        pdfs: Array.isArray(pdfs) ? pdfs : [],
        roadmaps: Array.isArray(roadmaps) ? roadmaps : [],
        interviews: Array.isArray(interviews) ? interviews : []
      });
    } catch (err) {
      setStatus(err.message);
    }
  }

  async function markView(type, id) {
    const map = {
      pdfs: `/pdfs/${id}/view/`,
      roadmaps: `/roadmaps/${id}/view/`,
      interviews: `/interviews/${id}/view/`
    };

    try {
      await request(map[type], { method: "POST", auth: true });
      await loadLibrary();
    } catch (err) {
      setStatus(err.message);
    }
  }

  async function downloadItem(type, id) {
    const map = {
      pdfs: `/pdfs/${id}/download/`,
      roadmaps: `/roadmaps/${id}/download/`,
      interviews: `/interviews/${id}/download/`
    };

    try {
      const data = await request(map[type], { method: "POST", auth: true });
      if (data?.url) window.open(data.url, "_blank", "noopener,noreferrer");
      await loadLibrary();
    } catch (err) {
      setStatus(err.message);
    }
  }

  async function handlePdfUpload(e) {
    e.preventDefault();
    const fd = new FormData();
    fd.append("title", pdfUpload.title);
    fd.append("file", pdfUpload.file);
    fd.append("image", pdfUpload.image);

    try {
      await request("/pdfs/", { method: "POST", body: fd, auth: true, isForm: true });
      setStatus("PDF submitted for approval.");
      setPdfUpload({ title: "", file: null, image: null });
      await loadLibrary();
    } catch (err) {
      setStatus(err.message);
    }
  }

  async function handleRoadmapUpload(e) {
    e.preventDefault();
    const fd = new FormData();
    fd.append("title", roadmapUpload.title);
    fd.append("description", roadmapUpload.description);
    fd.append("image", roadmapUpload.image);

    try {
      await request("/roadmaps/", { method: "POST", body: fd, auth: true, isForm: true });
      setStatus("Roadmap submitted for approval.");
      setRoadmapUpload({ title: "", description: "", image: null });
      await loadLibrary();
    } catch (err) {
      setStatus(err.message);
    }
  }

  async function handleInterviewUpload(e) {
    e.preventDefault();
    const fd = new FormData();
    fd.append("company", interviewUpload.company);
    fd.append("role", interviewUpload.role);
    fd.append("file", interviewUpload.file);

    try {
      await request("/interviews/", { method: "POST", body: fd, auth: true, isForm: true });
      setStatus("Interview PDF submitted for approval.");
      setInterviewUpload({ company: "", role: "", file: null });
      await loadLibrary();
    } catch (err) {
      setStatus(err.message);
    }
  }

  async function adminAction(type, id, action) {
    const path = `/admin/${type}/${id}/${action}/`;
    try {
      await request(path, { method: "POST", auth: true });
      setStatus(`${type.slice(0, -1)} ${action}d.`);
      await loadPending();
      await loadLibrary();
    } catch (err) {
      setStatus(err.message);
    }
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div className="hero-glow" />
        <div>
          <p className="eyebrow">React + Django + Axios</p>
          <h1>AstraVault Nexus</h1>
          <p className="hero-text">A premium command center for learning assets, upload workflows, and moderation.</p>
          <div className="metric-row">
            <span className="metric-chip">Approved {counts.total}</span>
            <span className="metric-chip">Pending {counts.pending}</span>
            {isAdmin && <span className="metric-chip">Admin Mode</span>}
          </div>
        </div>

        <div className="hero-controls">
          <label>
            API Base
            <input value={apiBase} onChange={(e) => setApiBase(e.target.value)} placeholder={DEFAULT_API} />
          </label>
          {token ? (
            <button className="danger" onClick={logout}>Logout {user ? `(${user})` : ""}</button>
          ) : (
            <span className="tag">Not logged in</span>
          )}
        </div>
      </header>

      {!token && (
        <section className="panel auth-panel">
          <div className="tab-row">
            <button className={authMode === "login" ? "active" : ""} onClick={() => setAuthMode("login")}>Login</button>
            <button className={authMode === "signup" ? "active" : ""} onClick={() => setAuthMode("signup")}>Signup</button>
          </div>
          <form onSubmit={handleAuthSubmit} className="form-grid">
            <input placeholder="Username" value={authForm.username} onChange={(e) => setAuthForm((s) => ({ ...s, username: e.target.value }))} required />
            {authMode === "signup" && (
              <input type="email" placeholder="Email" value={authForm.email} onChange={(e) => setAuthForm((s) => ({ ...s, email: e.target.value }))} required />
            )}
            <input type="password" placeholder="Password" value={authForm.password} onChange={(e) => setAuthForm((s) => ({ ...s, password: e.target.value }))} required />
            <button type="submit">{authMode === "login" ? "Login" : "Create Account"}</button>
          </form>
        </section>
      )}

      {token && (
        <>
          <nav className="panel nav-panel">
            <div className="tab-row">
              {tabs.map((tab) => (
                <button key={tab.id} className={activeTab === tab.id ? "active" : ""} onClick={() => setActiveTab(tab.id)}>
                  {tab.label}
                </button>
              ))}
            </div>
          </nav>

          {activeTab === "library" && (
            <section className="panel">
              <div className="section-head">
                <h2>Approved Library</h2>
                <p className="muted">Browse and track engagement across your approved resources.</p>
              </div>
              <div className="content-grid">
                <CardList title="PDFs" items={library.pdfs} onView={(id) => markView("pdfs", id)} onDownload={(id) => downloadItem("pdfs", id)} primary="title" secondary={(item) => `Views ${item.view_count} | Downloads ${item.download_count}`} />
                <CardList title="Roadmaps" items={library.roadmaps} onView={(id) => markView("roadmaps", id)} onDownload={(id) => downloadItem("roadmaps", id)} primary="title" secondary={(item) => `Views ${item.view_count} | Downloads ${item.download_count}`} />
                <CardList title="Interview PDFs" items={library.interviews} onView={(id) => markView("interviews", id)} onDownload={(id) => downloadItem("interviews", id)} primary={(item) => `${item.company} - ${item.role}`} secondary={(item) => `Views ${item.view_count} | Downloads ${item.download_count}`} />
              </div>
            </section>
          )}

          {activeTab === "upload" && (
            <section className="panel">
              <div className="section-head">
                <h2>Creator Studio</h2>
                <p className="muted">Submit polished assets for moderation using a clean publishing flow.</p>
              </div>
              <div className="content-grid">
                <form className="card form-card" onSubmit={handlePdfUpload}>
                  <h3>Upload PDF</h3>
                  <input placeholder="Title" value={pdfUpload.title} onChange={(e) => setPdfUpload((s) => ({ ...s, title: e.target.value }))} required />
                  <input type="file" accept="application/pdf" onChange={(e) => setPdfUpload((s) => ({ ...s, file: e.target.files?.[0] || null }))} required />
                  <input type="file" accept="image/*" onChange={(e) => setPdfUpload((s) => ({ ...s, image: e.target.files?.[0] || null }))} required />
                  <button type="submit">Submit PDF</button>
                </form>

                <form className="card form-card" onSubmit={handleRoadmapUpload}>
                  <h3>Upload Roadmap</h3>
                  <input placeholder="Title" value={roadmapUpload.title} onChange={(e) => setRoadmapUpload((s) => ({ ...s, title: e.target.value }))} required />
                  <textarea placeholder="Description" value={roadmapUpload.description} onChange={(e) => setRoadmapUpload((s) => ({ ...s, description: e.target.value }))} required />
                  <input type="file" accept="image/*" onChange={(e) => setRoadmapUpload((s) => ({ ...s, image: e.target.files?.[0] || null }))} required />
                  <button type="submit">Submit Roadmap</button>
                </form>

                <form className="card form-card" onSubmit={handleInterviewUpload}>
                  <h3>Upload Interview PDF</h3>
                  <input placeholder="Company" value={interviewUpload.company} onChange={(e) => setInterviewUpload((s) => ({ ...s, company: e.target.value }))} required />
                  <input placeholder="Role" value={interviewUpload.role} onChange={(e) => setInterviewUpload((s) => ({ ...s, role: e.target.value }))} required />
                  <input type="file" accept="application/pdf" onChange={(e) => setInterviewUpload((s) => ({ ...s, file: e.target.files?.[0] || null }))} required />
                  <button type="submit">Submit Interview PDF</button>
                </form>
              </div>
            </section>
          )}

          {activeTab === "admin" && (
            <section className="panel">
              <div className="section-head">
                <h2>Command Deck</h2>
                <p className="muted">Approve or reject pending content before it appears in the public vault.</p>
              </div>
              {!isAdmin && <p className="muted">Only admin users can access moderation endpoints.</p>}
              {isAdmin && (
                <div className="content-grid">
                  <AdminList title="Pending PDFs" items={pending.pdfs} primary="title" onApprove={(id) => adminAction("pdfs", id, "approve")} onReject={(id) => adminAction("pdfs", id, "reject")} />
                  <AdminList title="Pending Roadmaps" items={pending.roadmaps} primary="title" onApprove={(id) => adminAction("roadmaps", id, "approve")} onReject={(id) => adminAction("roadmaps", id, "reject")} />
                  <AdminList title="Pending Interviews" items={pending.interviews} primary={(item) => `${item.company} - ${item.role}`} onApprove={(id) => adminAction("interviews", id, "approve")} onReject={(id) => adminAction("interviews", id, "reject")} />
                </div>
              )}
            </section>
          )}
        </>
      )}

      <footer className="status-bar">{status || "Ready."}</footer>
    </div>
  );
}

function resolveText(item, primary) {
  return typeof primary === "function" ? primary(item) : item[primary];
}

function CardList({ title, items, onView, onDownload, primary, secondary }) {
  return (
    <section className="card">
      <h3>{title}</h3>
      {items.length === 0 && <p className="muted">No records found.</p>}
      {items.map((item) => (
        <article key={item.id} className="row">
          <div>
            <strong>{resolveText(item, primary)}</strong>
            <p>{secondary(item)}</p>
          </div>
          <div className="action-row">
            <button className="ghost" onClick={() => onView(item.id)}>View +1</button>
            <button onClick={() => onDownload(item.id)}>Download</button>
          </div>
        </article>
      ))}
    </section>
  );
}

function AdminList({ title, items, primary, onApprove, onReject }) {
  return (
    <section className="card">
      <h3>{title}</h3>
      {items.length === 0 && <p className="muted">Nothing pending.</p>}
      {items.map((item) => (
        <article key={item.id} className="row">
          <div>
            <strong>{resolveText(item, primary)}</strong>
            <p>ID: {item.id}</p>
          </div>
          <div className="action-row">
            <button onClick={() => onApprove(item.id)}>Approve</button>
            <button className="danger" onClick={() => onReject(item.id)}>Reject</button>
          </div>
        </article>
      ))}
    </section>
  );
}

export default App;
