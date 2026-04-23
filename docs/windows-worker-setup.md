# Windows Worker Setup (Real HEC-RAS)

## Purpose
The Dockerized API/frontend stack runs cross-platform, but HEC-RAS execution must happen on a Windows node.

## Steps

1. Install Python 3.11 and `pip install -r apps/windows-worker/requirements.txt`.
2. Install HEC-RAS and verify manual project execution.
3. Configure env vars:
   - `API_BASE_URL`
   - `REDIS_URL`
   - `HECRAS_PROJECT_TEMPLATE`
4. Implement automation in `apps/windows-worker/worker/main.py` under `TODO_HECRAS_*` markers.
5. Start worker process (customized for your queue contract).

## Required Wiring Points

- Read job payload from Redis queue.
- Fetch workspace input files from API or shared storage.
- Execute HEC-RAS with template plan and scenario data.
- Upload generated outputs back to API storage endpoint.
- Post status events (`running`, `failed`, `completed`) to API.

## Security Notes

- Run worker under restricted service account.
- Restrict workspace paths and sanitize incoming filenames.
- Store credentials in Windows secret manager or environment vault.
