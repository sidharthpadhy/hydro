import type { JobDetails } from "@/types";

export function JobTimeline({ job }: { job: JobDetails | null }) {
  if (!job) return <div>No job yet.</div>;
  return (
    <div>
      <h3>Status: {job.status}</h3>
      <ul>
        {job.events.map((e) => (
          <li key={`${e.created_at}-${e.message}`}>
            [{e.status}] {e.message}
          </li>
        ))}
      </ul>
    </div>
  );
}
