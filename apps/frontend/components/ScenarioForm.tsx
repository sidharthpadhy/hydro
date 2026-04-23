"use client";

import { useState } from "react";
import type { ScenarioInput } from "@/types";

type Props = { onSubmit: (value: ScenarioInput) => void };

export function ScenarioForm({ onSubmit }: Props) {
  const [form, setForm] = useState<ScenarioInput>({
    peak_flow_cms: 250,
    mannings_n: 0.04,
    upstream_bc: "flow hydrograph",
    downstream_bc: "normal depth",
    simulation_start: "2026-01-01T00:00:00Z",
    simulation_end: "2026-01-02T00:00:00Z",
    mesh_cell_size: 30,
    crs: "EPSG:3857",
    units: "metric",
  });

  return (
    <div style={{ border: "1px solid #ccc", borderRadius: 8, padding: 12 }}>
      <h3>25-year Scenario Parameters</h3>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
        {Object.entries(form).map(([k, v]) => (
          <label key={k} style={{ display: "flex", flexDirection: "column" }}>
            {k}
            <input
              value={String(v)}
              onChange={(e) =>
                setForm((old) => ({ ...old, [k]: typeof v === "number" ? Number(e.target.value) : e.target.value }))
              }
            />
          </label>
        ))}
      </div>
      <button onClick={() => onSubmit(form)} style={{ marginTop: 12 }}>
        Launch Job
      </button>
    </div>
  );
}
