"use client";

import { useRef, useState } from "react";

type Props = {
  title: string;
  accept: string;
  onFile: (file: File) => Promise<void>;
  onError?: (message: string) => void;
};

export function UploadCard({ title, accept, onFile, onError }: Props) {
  const ref = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);

  async function handleFile(file: File | undefined) {
    if (!file || isUploading) return;
    setIsUploading(true);
    onError?.("");
    try {
      await onFile(file);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      onError?.(message);
    } finally {
      setIsUploading(false);
      if (ref.current) ref.current.value = "";
    }
  }

  return (
    <div style={{ border: "1px solid #ccc", padding: 12, borderRadius: 8 }}>
      <h3>{title}</h3>
      <div
        style={{
          border: "1px dashed #888",
          padding: 24,
          cursor: isUploading ? "wait" : "pointer",
          opacity: isUploading ? 0.7 : 1,
        }}
        onClick={() => {
          if (!isUploading) ref.current?.click();
        }}
      >
        {isUploading ? "Uploading..." : "Drag/drop or click to upload"}
      </div>
      <input
        ref={ref}
        type="file"
        accept={accept}
        style={{ display: "none" }}
        onChange={(e) => {
          void handleFile(e.target.files?.[0]);
        }}
      />
    </div>
  );
}
