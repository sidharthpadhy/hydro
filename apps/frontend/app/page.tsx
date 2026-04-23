"use client";

import { useState } from "react";
import { JobTimeline } from "@/components/JobTimeline";
import { MapPreview } from "@/components/MapPreview";
import { ScenarioForm } from "@/components/ScenarioForm";
import { UploadCard } from "@/components/UploadCard";
import { createJob, getJob, getResults, uploadFile } from "@/lib/api";
import type { JobDetails, ScenarioInput, UploadMeta } from "@/types";

export default function HomePage() {
  const [dem, setDem] = useState<UploadMeta | null>(null);
  const [streams, setStreams] = useState<UploadMeta | null>(null);
  const [job, setJob] = useState<JobDetails | null>(null);
  const [results, setResults] = useState<Array<{ asset_type: string; file_name: string; download_url: string }>>([]);
  const [error, setError] = useState<string>("");

  const launchJob = async (parameters: ScenarioInput) => {
    if (!dem || !streams) return setError("Upload both DEM and streams first.");
    setError("");
    try {
      const created = await createJob(dem.asset_id, streams.asset_id, parameters);
      const details = await getJob(created.job_id);
      setJob(details);
      const out = await getResults(created.job_id);
      setResults(out);
    } catch (e) {
      setError(String(e));
    }
  };

  return (
    <main style={{ maxWidth: 1100, margin: "0 auto", padding: 24, fontFamily: "Arial" }}>
      <h1>Automated Flood Analysis Dashboard</h1>
      <p>HEC-RAS hydraulic workflow (25-year scenario) with required scenario inputs.</p>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <UploadCard
          title="Upload DEM (.tif/.tiff)"
          accept=".tif,.tiff"
          onError={setError}
          onFile={async (file) => setDem(await uploadFile("/api/uploads/dem", file))}
        />
        <UploadCard
          title="Upload Streams (.kml)"
          accept=".kml"
          onError={setError}
          onFile={async (file) => setStreams(await uploadFile("/api/uploads/streams", file))}
        />
      </div>

      <section style={{ marginTop: 16 }}>
        <h2>Upload Metadata</h2>
        <pre>{JSON.stringify({ dem, streams }, null, 2)}</pre>
      </section>

      <ScenarioForm onSubmit={launchJob} />
      <JobTimeline job={job} />

      <section>
        <h3>Result Downloads</h3>
        <ul>
          {results.map((r) => (
            <li key={r.download_url}>
              {r.asset_type}: <a href={`http://localhost:8000${r.download_url}`}>{r.file_name}</a>
            </li>
          ))}
        </ul>
      </section>

      <MapPreview />
    </main>
  );
}
