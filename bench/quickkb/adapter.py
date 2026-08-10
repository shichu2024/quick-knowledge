"""QuickkbAdapter — wires dataloader + rollout into SkillOpt's EnvAdapter.

For MVP this adapter is consumed by our own ``bench/run_eval.py`` entry
script rather than SkillOpt's ``scripts/eval_only.py`` registry. The
adapter shape is kept SkillOpt-compatible so a future commit can register
it into ``_ENV_REGISTRY`` without rewiring.
"""
from __future__ import annotations

from skillopt.datasets.base import BatchSpec
from skillopt.envs.base import EnvAdapter

from .dataloader import QuickkbDataLoader
from .rollout import run_batch


class QuickkbAdapter(EnvAdapter):
    """Adapter for quick-knowledge skill benchmarks.

    Parameters
    ----------
    skill : str
        Skill slug. ``"capture"`` for point-tests (45 cases),
        ``"flow"`` for J-class end-to-end (6 cases).
    cases_root : str
        Root directory of cases (default ``bench/cases``).
    """

    def __init__(
        self,
        skill: str = "capture",
        cases_root: str = "bench/cases",
        split_dir: str = "",
        data_path: str = "",
        split_mode: str = "ratio",
        split_ratio: str = "3:1:1",
        split_seed: int = 42,
        split_output_dir: str = "",
        workers: int = 1,
        analyst_workers: int = 1,
        failure_only: bool = False,
        minibatch_size: int = 8,
        edit_budget: int = 4,
        seed: int = 42,
        limit: int = 0,
        max_completion_tokens: int = 4096,
        **kwargs,
    ) -> None:
        self.skill = skill
        self.workers = workers
        self.analyst_workers = analyst_workers
        self.failure_only = failure_only
        self.minibatch_size = minibatch_size
        self.edit_budget = edit_budget
        self.max_completion_tokens = int(max_completion_tokens)
        self.dataloader = QuickkbDataLoader(
            skill=skill,
            cases_root=cases_root,
            split_ratio=split_ratio,
            split_seed=split_seed,
            split_output_dir=split_output_dir,
            seed=seed,
            limit=limit,
        )

    # ── Lifecycle ────────────────────────────────────────────────────

    def setup(self, cfg: dict) -> None:
        super().setup(cfg)
        self.dataloader.setup(cfg)

    def get_dataloader(self):
        return self.dataloader

    # ── Batch → env manager ──────────────────────────────────────────

    def build_env_from_batch(self, batch: BatchSpec, **kwargs):
        return list(batch.payload or [])

    def build_train_env(self, batch_size: int, seed: int, **kwargs):
        batch = self.dataloader.build_train_batch(batch_size=batch_size, seed=seed, **kwargs)
        return self.build_env_from_batch(batch, **kwargs)

    def build_eval_env(self, env_num: int, split: str, seed: int, **kwargs):
        batch = self.dataloader.build_eval_batch(env_num=env_num, split=split, seed=seed, **kwargs)
        return self.build_env_from_batch(batch, **kwargs)

    # ── Rollout ──────────────────────────────────────────────────────

    def rollout(
        self,
        env_manager,
        skill_content: str,
        out_dir: str,
        **kwargs,
    ) -> list[dict]:
        items: list[dict] = env_manager
        return run_batch(
            items=items,
            skill_content=skill_content,
            out_root=out_dir,
            workers=self.workers,
            max_completion_tokens=self.max_completion_tokens,
            extra_context=kwargs.get("extra_context", ""),
        )

    # ── SkillOpt metadata ────────────────────────────────────────────

    def get_task_types(self) -> list[str]:
        seen: list[str] = []
        for item in (
            self.dataloader.train_items
            + self.dataloader.val_items
            + self.dataloader.test_items
        ):
            task_type = str(item.get("dimension") or self.skill)
            if task_type not in seen:
                seen.append(task_type)
        return seen or [self.skill]
