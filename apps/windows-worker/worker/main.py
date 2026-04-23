"""Windows worker entrypoint.

Integration points for real HEC-RAS automation are marked with TODO_HECRAS tags.
"""

from dataclasses import dataclass


@dataclass
class WorkerConfig:
    api_base_url: str
    redis_url: str
    hecras_project_template: str


class RealHecRasAdapter:
    def run_model(self, job_config: dict) -> dict:
        """Run model on Windows with HEC-RAS.

        TODO_HECRAS_1: Open HEC-RAS project template via COM automation or CLI-compatible wrapper.
        TODO_HECRAS_2: Inject terrain, geometry, boundary conditions, and plan.
        TODO_HECRAS_3: Launch computation and await completion.
        TODO_HECRAS_4: Export depth/WSE rasters and logs.
        """
        raise NotImplementedError("Wire to real HEC-RAS automation on Windows host")
