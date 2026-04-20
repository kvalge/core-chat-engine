import { useState, useRef } from "react";

interface FileUploadProps {
  onFileSelect?: (file: File) => void;
  conversationId?: number;
  messageId?: number;
}

export default function FileUpload({ onFileSelect, conversationId, messageId }: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ["text/plain", "application/pdf", "image/jpeg", "image/png", "image/gif", "image/webp"];
    if (!allowedTypes.includes(file.type)) {
      setError("Unsupported file type. Allowed: txt, pdf, jpg, png, gif, webp");
      return;
    }

    // Validate size (25MB)
    if (file.size > 25 * 1024 * 1024) {
      setError("File too large. Maximum size is 25MB");
      return;
    }

    setError(null);

    // Create preview for images
    if (file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = () => setPreview(reader.result as string);
      reader.readAsDataURL(file);
    }

    // If we have conversation and message IDs, upload to server
    if (conversationId && messageId) {
      setUploading(true);
      try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(
          `/api/upload?conversation_id=${conversationId}&message_id=${messageId}`,
          {
            method: "POST",
            body: formData,
          }
        );

        if (!response.ok) {
          const data = await response.json();
          setError(data.detail || "Upload failed");
          return;
        }

        onFileSelect?.(file);
      } catch (err) {
        setError("Upload failed");
        console.error(err);
      } finally {
        setUploading(false);
      }
    } else {
      onFileSelect?.(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div style={{ display: "inline-block", position: "relative" }}>
      <input
        ref={fileInputRef}
        type="file"
        accept=".txt,.pdf,.jpg,.jpeg,.png,.gif,.webp"
        onChange={handleFileChange}
        style={{ display: "none" }}
      />

      <button
        type="button"
        onClick={handleClick}
        disabled={uploading}
        style={{
          padding: "0.5rem",
          backgroundColor: "transparent",
          border: "1px dashed #ccc",
          borderRadius: "0.25rem",
          cursor: uploading ? "not-allowed" : "pointer",
          opacity: uploading ? 0.5 : 1,
        }}
        title="Upload file (txt, pdf, images)"
      >
        📎
      </button>

      {error && (
        <div
          style={{
            position: "absolute",
            bottom: "100%",
            left: 0,
            backgroundColor: "#fee2e2",
            color: "#dc2626",
            padding: "0.5rem",
            borderRadius: "0.25rem",
            fontSize: "0.75rem",
            whiteSpace: "nowrap",
            zIndex: 10,
          }}
        >
          {error}
        </div>
      )}

      {preview && (
        <div
          style={{
            position: "absolute",
            bottom: "100%",
            left: 0,
            padding: "0.5rem",
            zIndex: 10,
          }}
        >
          <img
            src={preview}
            alt="Preview"
            style={{
              maxWidth: "200px",
              maxHeight: "200px",
              borderRadius: "0.25rem",
            }}
          />
        </div>
      )}
    </div>
  );
}