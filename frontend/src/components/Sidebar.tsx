import { useState, useEffect, useCallback } from "react";
import { deleteProject } from "../services/api";

interface Project {
  id: number;
  name: string;
}

interface SidebarProps {
  onNavigate: (page: "chat" | "settings") => void;
  currentPage: "chat" | "settings";
  selectedProjectId: number | null;
  onSelectProject: (id: number | null) => void;
}

export default function Sidebar({
  onNavigate,
  currentPage,
  selectedProjectId,
  onSelectProject,
}: SidebarProps) {
  const [projects, setProjects] = useState<Project[]>([]);

  const fetchProjects = useCallback(async (): Promise<Project[]> => {
    const response = await fetch("/api/projects");
    if (!response.ok) {
      const text = await response.text();
      console.error("Failed to load projects:", response.status, text);
      return [];
    }
    return response.json() as Promise<Project[]>;
  }, []);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const data = await fetchProjects();
      if (cancelled) return;
      setProjects(data);
      if (data.length === 0) {
        onSelectProject(null);
      } else if (
        selectedProjectId == null ||
        !data.some((p) => p.id === selectedProjectId)
      ) {
        onSelectProject(data[0].id);
      }
    })();
    return () => {
      cancelled = true;
    };
    // Intentionally only bootstrap when the app mounts (or Strict Mode remount).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fetchProjects, onSelectProject]);

  const createProject = async () => {
    const name = prompt("Enter project name:");
    if (!name?.trim()) return;

    try {
      const response = await fetch("/api/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name.trim() }),
      });
      if (!response.ok) {
        let detail = `HTTP ${response.status}`;
        try {
          const err = (await response.json()) as { detail?: unknown };
          if (typeof err.detail === "string") detail = err.detail;
          else if (Array.isArray(err.detail))
            detail = err.detail.map((d: { msg?: string }) => d.msg ?? "").join("; ");
        } catch {
          detail = await response.text();
        }
        alert(`Could not create project: ${detail}`);
        return;
      }
      const created: Project = await response.json();
      const data = await fetchProjects();
      setProjects(data);
      onSelectProject(created.id);
    } catch (error) {
      console.error("Error creating project:", error);
      alert(error instanceof Error ? error.message : "Could not create project");
    }
  };

  const handleDeleteProject = async (e: React.MouseEvent, project: Project) => {
    e.stopPropagation();
    if (
      !confirm(
        `Delete project "${project.name}" and all of its chats? This cannot be undone.`
      )
    )
      return;
    try {
      await deleteProject(project.id);
      const data = await fetchProjects();
      setProjects(data);
      if (selectedProjectId === project.id) {
        onSelectProject(data.length > 0 ? data[0].id : null);
      }
    } catch (error) {
      console.error("Error deleting project:", error);
      alert(error instanceof Error ? error.message : "Could not delete project");
    }
  };

  return (
    <aside
      style={{
        width: "220px",
        borderRight: "1px solid #e5e7eb",
        padding: "1rem",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <h2 style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>Projects</h2>

      <div style={{ flex: 1, overflow: "auto" }}>
        {projects.map((project) => (
          <div
            key={project.id}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.35rem",
              marginBottom: "0.25rem",
              borderRadius: "0.25rem",
              backgroundColor:
                selectedProjectId === project.id ? "#e5e7eb" : "transparent",
              padding: "0.15rem 0.35rem 0.15rem 0.5rem",
            }}
          >
            <div
              onClick={() => onSelectProject(project.id)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelectProject(project.id);
                }
              }}
              role="button"
              tabIndex={0}
              style={{
                flex: 1,
                padding: "0.35rem 0",
                cursor: "pointer",
                minWidth: 0,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {project.name}
            </div>
            <button
              type="button"
              title="Delete project"
              aria-label={`Delete project ${project.name}`}
              onClick={(e) => void handleDeleteProject(e, project)}
              style={{
                flexShrink: 0,
                padding: "0.2rem 0.45rem",
                fontSize: "0.75rem",
                lineHeight: 1,
                border: "none",
                borderRadius: "0.25rem",
                backgroundColor: "#fecaca",
                color: "#991b1b",
                cursor: "pointer",
              }}
            >
              ×
            </button>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={() => void createProject()}
        style={{
          padding: "0.5rem",
          marginTop: "0.5rem",
          backgroundColor: "#22c55e",
          color: "white",
          border: "none",
          borderRadius: "0.25rem",
          cursor: "pointer",
        }}
      >
        + New Project
      </button>

      <div
        style={{
          borderTop: "1px solid #e5e7eb",
          marginTop: "1rem",
          paddingTop: "1rem",
        }}
      >
        <button
          type="button"
          onClick={() => onNavigate("chat")}
          style={{
            display: "block",
            width: "100%",
            padding: "0.5rem",
            textAlign: "left",
            backgroundColor: currentPage === "chat" ? "#e5e7eb" : "transparent",
            border: "none",
            cursor: "pointer",
          }}
        >
          Chat
        </button>
        <button
          type="button"
          onClick={() => onNavigate("settings")}
          style={{
            display: "block",
            width: "100%",
            padding: "0.5rem",
            textAlign: "left",
            backgroundColor: currentPage === "settings" ? "#e5e7eb" : "transparent",
            border: "none",
            cursor: "pointer",
          }}
        >
          Settings
        </button>
      </div>
    </aside>
  );
}
