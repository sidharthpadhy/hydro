import type { JobDetails, ScenarioInput, UploadMeta } from "@/types";

const API = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function uploadFile(endpoint: string, file: File): Promise<UploadMeta> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API}${endpoint}`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function createJob(demId: string, streamId: string, parameters: ScenarioInput) {
  const res = await fetch(`${API}/api/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dem_asset_id: demId, streams_asset_id: streamId, parameters }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getJob(jobId: string): Promise<JobDetails> {
  const res = await fetch(`${API}/api/jobs/${jobId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getResults(jobId: string) {
  const res = await fetch(`${API}/api/jobs/${jobId}/results`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
