#!/usr/bin/env python
"""High-level interface for discovering and ingesting photo-z models.

Provides preset configurations for DP1 and DP2 data releases, locates model
files on disk by algorithm name, and delegates the actual Butler ingestion to
:func:`rail_export.butler_ingest_models.ingest_models`.

Can be invoked as a script::

    python -m rail_export.ingest dp1
"""

import sys
import glob
from pathlib import Path

from lsst.daf.butler import Butler

from rail_export.butler_ingest_models import ingest_models


# Supported photo-z algorithms whose trained models can be ingested.
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

# DP1 ingestion parameters (ComCam, 6-band configuration on SLAC SDF).
DP1_CONFIG: dict[str, str] = dict(
    butler="/repo/dp1",
    model_base_dir="/sdf/data/rubin/shared/pz/users/echarles/work/dp1",
    model_base_col="pretrained_models/pz/dp1",
    version="v2",
    flavor="dp1_6band",
    selection="gold",
    instrument_name="LSSTComCam",
)

# DP2 ingestion parameters (LSSTCam, baseline configuration on SLAC SDF).
DP2_CONFIG: dict[str, str] = dict(
    butler="dp2_prep",
    model_base_dir="/sdf/data/rubin/shared/pz/models",
    model_base_col="u/echarles/pretrained_models/pz",
    version="dp2_v3",
    flavor="baseline",
    selection="gold",
    instrument_name="LSSTCam",
)

# Lookup table of available target configurations.
ALL_CONFIGS: dict[str, dict[str, str]] = dict(
    dp1=DP1_CONFIG,
    dp2=DP2_CONFIG,
)


def ingest(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    butler: Butler,
    algos: list[str],
    model_base_dir: str | Path,
    model_base_col: str,
    version: str,
    flavor: str,
    selection: str = "gold",
    instrument_name: str = "LSSTCam",
) -> int:
    """Discover model files on disk and ingest them into a Butler collection.

    Constructs the on-disk model directory and the target Butler collection
    path from the version/flavor/selection parameters, then globs for files
    matching each algorithm name and ingests them.

    Parameters
    ----------
    butler : Butler
        A writeable Butler instance.
    algos : list[str]
        Algorithm names to ingest (e.g. ``["knn", "bpz"]``).
    model_base_dir : str or Path
        Root directory containing model subdirectories.
    model_base_col : str
        Base Butler collection path (version/selection/flavor are appended).
    version : str
        Model version identifier (e.g. ``"v2"``).
    flavor : str
        Training flavor (e.g. ``"dp1_6band"``, ``"baseline"``).
    selection : str, optional
        Sample selection label. Defaults to ``"gold"``.
    instrument_name : str, optional
        Instrument dimension value. Defaults to ``"LSSTCam"``.

    Returns
    -------
    int
        Exit code (0 on success).
    """
    # Build paths: e.g. /sdf/.../models_v2_dp1_6band
    model_dir = Path(model_base_dir) / f"models_{version}_{flavor}"
    # Build collection: e.g. pretrained_models/pz/dp1/v2/gold/dp1_6band
    model_col = f"{model_base_col}/{version}/{selection}/{flavor}"

    # Glob for files matching each algorithm name in the model directory.
    models: dict[str, list[str | Path]] = {}
    for algo in algos:
        models[algo] = list(glob.glob(f"{model_dir}/*{algo}*"))

    return ingest_models(butler, model_col, models, instrument_name)


if __name__ == "__main__":
    # CLI entry point: accepts an optional target name (default: "dp1").
    target = sys.argv[1] if len(sys.argv) > 1 else "dp1"

    try:
        the_config = ALL_CONFIGS[target]
    except KeyError:
        print(f"Unknown target: {target}")
        sys.exit(1)

    # Pop butler alias separately since it's used for Butler construction,
    # not passed through to ingest().
    butler_alias = the_config.pop("butler")
    b = Butler.from_config(butler_alias, writeable=True)
    ingest(b, ALGOS, **the_config)
