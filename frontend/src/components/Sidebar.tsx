import { useState, useEffect } from "react";

interface Project {
  id: number;
  name: string;
}

interface SidebarProps {
  onNavigate: (page: "chat" | "settings") => void;
  currentPage: "chat" | "settings";
}

export default function Sidebar({ onNavigate, currentPage }: SidebarProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<number | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await fetch("/api/projects");
      const data = await response.json();
      setProjects(data);
      if (data.length > 0 && !selectedProject) {
        setSelectedProject(data[0].id);
      }
    } catch (error) {
      console.error("Error loading projects:", error);
    }
  };

  const createProject = async () => {
    const name = prompt("Enter project name:");
    if (!name) return;

    try {
      const response = await fetch("/api/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      if (response.ok) {
        loadProjects();
      }
    } catch (error) {
      console.error("Error creating project:", error);
    }
  };

  return (
    <aside
      style={{
        width: "200px",
        borderRight: "1px solid #e5e7eb",
        padding: "1rem",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <h2 style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>
        Projects
      </h2>

      <div style={{ flex: 1, overflow: "auto" }}>
        {projects.map((project) => (
          <div
            key={project.id}
            onClick={() => setSelectedProject(project.id)}
            style={{
              padding: "0.5rem",
              borderRadius: "0.25rem",
              cursor: "pointer",
              backgroundColor: selectedProject === project.id ? "#e5e7eb" : "transparent",
              marginBottom: "0.25rem",
            }}
          >
            {project.name}
          </div>
        ))}
      </div>

      <button
        onClick={createProject}
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

      <div style={{ borderTop: "1px solid #e5e7eb", marginTop: "1rem", paddingTop: "1rem" }}>
        <button
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