export type UploadMeta = {
  asset_id: string;
  filename: string;
  metadata: Record<string, unknown>;
};

export type ScenarioInput = {
  peak_flow_cms: number;
  mannings_n: number;
  upstream_bc: string;
  downstream_bc: string;
  simulation_start: string;
  simulation_end: string;
  mesh_cell_size: number;
  crs: string;
  units: string;
  hydrograph_json?: Record<string, unknown>;
};

export type JobDetails = {
  job_id: string;
  status: string;
  created_at: string;
  events: Array<{ status: string; message: string; created_at: string }>;
};
