import { useState, useEffect } from "react";

interface Backend {
  id: number;
  name: string;
  base_url: string;
  models: string[];
  is_default: boolean;
}

export default function BackendConfig() {
  const [backends, setBackends] = useState<Backend[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    base_url: "http://localhost:11434",
    api_key: "",
    models: "",
  });
  const [testing, setTesting] = useState<number | null>(null);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  useEffect(() => {
    loadBackends();
  }, []);

  const loadBackends = async () => {
    try {
      const response = await fetch("/api/backends");
      const data = await response.json();
      setBackends(data);
    } catch (error) {
      console.error("Error loading backends:", error);
    }
  };

  const addBackend = async () => {
    if (!formData.name || !formData.base_url) return;

    try {
      await fetch("/api/backends", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          models: formData.models.split(",").map((m) => m.trim()).filter(Boolean),
        }),
      });
      setShowForm(false);
      setFormData({ name: "", base_url: "http://localhost:11434", api_key: "", models: "" });
      loadBackends();
    } catch (error) {
      console.error("Error adding backend:", error);
    }
  };

  const testConnection = async (backendId: number) => {
    setTesting(backendId);
    setTestResult(null);

    try {
      const response = await fetch(`/api/backends/${backendId}/test`, {
        method: "POST",
      });
      const data = await response.json();
      setTestResult(data);
    } catch (error) {
      setTestResult({ success: false, message: String(error) });
    } finally {
      setTesting(null);
    }
  };

  const deleteBackend = async (backendId: number) => {
    if (!confirm("Delete this backend?")) return;

    try {
      await fetch(`/api/backends/${backendId}`, { method: "DELETE" });
      loadBackends();
    } catch (error) {
      console.error("Error deleting backend:", error);
    }
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h2 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>
        Backend Configuration
      </h2>

      <button
        onClick={() => setShowForm(!showForm)}
        style={{
          padding: "0.5rem 1rem",
          backgroundColor: "#3b82f6",
          color: "white",
          border: "none",
          borderRadius: "0.25rem",
          cursor: "pointer",
        }}
      >
        {showForm ? "Cancel" : "+ Add Backend"}
      </button>

      {showForm && (
        <div style={{ marginTop: "1rem", padding: "1rem", border: "1px solid #ddd", borderRadius: "0.5rem" }}>
          <input
            type="text"
            placeholder="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            style={{ display: "block", width: "100%", marginBottom: "0.5rem", padding: "0.5rem" }}
          />
          <input
            type="text"
            placeholder="Base URL (e.g., http://localhost:11434)"
            value={formData.base_url}
            onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
            style={{ display: "block", width: "100%", marginBottom: "0.5rem", padding: "0.5rem" }}
          />
          <input
            type="password"
            placeholder="API Key (optional)"
            value={formData.api_key}
            onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
            style={{ display: "block", width: "100%", marginBottom: "0.5rem", padding: "0.5rem" }}
          />
          <input
            type="text"
            placeholder="Models (comma-separated)"
            value={formData.models}
            onChange={(e) => setFormData({ ...formData, models: e.target.value })}
            style={{ display: "block", width: "100%", marginBottom: "0.5rem", padding: "0.5rem" }}
          />
          <button
            onClick={addBackend}
            style={{ padding: "0.5rem 1rem", backgroundColor: "#22c55e", color: "white", border: "none", borderRadius: "0.25rem", cursor: "pointer" }}
          >
            Save
          </button>
        </div>
      )}

      <div style={{ marginTop: "1rem" }}>
        {backends.map((backend) => (
          <div
            key={backend.id}
            style={{
              padding: "1rem",
              border: "1px solid #e5e7eb",
              borderRadius: "0.5rem",
              marginBottom: "0.5rem",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <strong>{backend.name}</strong>
              {backend.is_default && <span style={{ fontSize: "0.75rem", backgroundColor: "#22c55e", color: "white", padding: "0.125rem 0.5rem", borderRadius: "1rem" }}>Default</span>}
            </div>
            <div style={{ fontSize: "0.875rem", color: "#666", marginTop: "0.25rem" }}>
              {backend.base_url}
            </div>
            <div style={{ fontSize: "0.875rem", color: "#666" }}>
              Models: {backend.models.join(", ") || "Any"}
            </div>
            <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.5rem" }}>
              <button
                onClick={() => testConnection(backend.id)}
                disabled={testing === backend.id}
                style={{ padding: "0.25rem 0.5rem", backgroundColor: "#e5e7eb", border: "none", borderRadius: "0.25rem", cursor: "pointer" }}
              >
                {testing === backend.id ? "Testing..." : "Test Connection"}
              </button>
              <button
                onClick={() => deleteBackend(backend.id)}
                style={{ padding: "0.25rem 0.5rem", backgroundColor: "#ef4444", color: "white", border: "none", borderRadius: "0.25rem", cursor: "pointer" }}
              >
                Delete
              </button>
            </div>
            {testResult && testing === null && (
              <div style={{ marginTop: "0.5rem", color: testResult.success ? "#22c55e" : "#ef4444" }}>
                {testResult.message}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}