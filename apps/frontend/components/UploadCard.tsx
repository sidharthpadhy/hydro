"use client";

import { useRef } from "react";

type Props = {
  title: string;
  accept: string;
  onFile: (file: File) => void;
};

export function UploadCard({ title, accept, onFile }: Props) {
  const ref = useRef<HTMLInputElement>(null);
  return (
    <div style={{ border: "1px solid #ccc", padding: 12, borderRadius: 8 }}>
      <h3>{title}</h3>
      <div
        style={{ border: "1px dashed #888", padding: 24, cursor: "pointer" }}
        onClick={() => ref.current?.click()}
      >
        Drag/drop or click to upload
      </div>
      <input
        ref={ref}
        type="file"
        accept={accept}
        style={{ display: "none" }}
        onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
      />
    </div>
  );
}
