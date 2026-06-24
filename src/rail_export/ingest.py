#!/usr/bin/env python
import sys
import glob
from pathlib import Path

from lsst.daf.butler import Butler

from rail_export.butler_ingest_models import ingest_models


ALGOS = [
    "knn",
    "gpz",
    "bpz",
    "fzboost",
    "dnf",
    "tpz",
    "cmnn",
    "lephare",
]

DP1_CONFIG: dict[str, str] = dict(
    butler="/repo/dp1",
    model_base_dir="/sdf/data/rubin/shared/pz/users/echarles/work/dp1",
    model_base_col="pretrained_models/pz/dp1",
    version="v2",
    flavor="dp1_6band",
    selection="gold",
    instrument_name="LSSTComCam",
)

DP2_CONFIG: dict[str, str] = dict(
    butler="dp2_prep",
    model_base_dir="/sdf/data/rubin/shared/pz/models",
    model_base_col="u/echarles/pretrained_models/pz",
    version="dp2_v3",
    flavor="baseline",
    selection="gold",
    instrument_name="LSSTCam",
)

ALL_CONFIGS: dict[str, dict[str, str]] = dict(
    dp1=DP1_CONFIG,
    dp2=DP2_CONFIG,
)


def ingest(
    butler: Butler,
    algos: list[str],
    model_base_dir: str | Path,
    model_base_col: str,
    version: str,
    flavor: str,
    selection: str = "gold",
    instrument_name: str = "LSSTCam",
) -> int:

    model_dir = Path(model_base_dir) / f"models_{version}_{flavor}"
    model_col = f"{model_base_col}/{version}/{selection}/{flavor}"

    models: dict[str, list[str | Path]] = {}
    for algo in algos:
        models[algo] = glob.glob(f"{model_dir}/*{algo}*")

    return ingest_models(butler, model_col, models, instrument_name)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "dp1"

    try:
        the_config = ALL_CONFIGS[target]
    except KeyError:
        print(f"Unknown target: {target}")
        sys.exit(1)

    butler_alias = the_config.pop("butler")
    b = Butler.from_config(butler_alias, writeable=True)
    ingest(b, ALGOS, **the_config)
