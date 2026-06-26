"""Low-level Butler ingestion of photo-z model files.

Registers per-algorithm dataset types (e.g. ``pzModel_knn``) as calibration
products dimensioned by instrument, then ingests the corresponding model files
into the specified Butler collection.
"""

from pathlib import Path

from lsst.daf.butler import (
    Butler,
    DataCoordinate,
    DatasetRef,
    DatasetType,
    DimensionGroup,
    FileDataset,
)


def ingest_models(
    butler: Butler,
    model_collection: str,
    models: dict[str, list[str | Path]],
    instrument_name: str = "LSSTCam",
) -> int:
    """Register dataset types and ingest model files into a Butler repository.

    For each algorithm in *models*, ensures that a calibration dataset type
    named ``pzModel_<algo>`` exists (creating and registering it if not), then
    ingests each associated file into *model_collection*.

    Parameters
    ----------
    butler : Butler
        A writeable Butler instance.
    model_collection : str
        The Butler RUN collection where models will be ingested
        (e.g. ``"pretrained_models/pz/dp1/v2/gold/dp1_6band"``).
    models : dict[str, list[str | Path]]
        Mapping of algorithm name to a list of model file paths to ingest.
    instrument_name : str, optional
        Instrument dimension value for the data coordinate.
        Defaults to ``"LSSTCam"``.

    Returns
    -------
    int
        Exit code (0 on success).
    """
    dim_universe = butler.dimensions
    # All photo-z models are dimensioned only by instrument.
    pzModel_dimension_group = DimensionGroup(
        dim_universe,
        ["instrument"],
    )

    for algo_, model_files in models.items():
        model_type = f"pzModel_{algo_}"

        # Look up existing dataset type; register a new one if absent.
        try:
            dataset_type = butler.registry.getDatasetType(model_type)
        except KeyError:
            dataset_type = None
        if dataset_type is None:
            dataset_type = DatasetType(
                model_type,
                dimensions=pzModel_dimension_group,
                storageClass="PZModel",
                isCalibration=True,
            )
            butler.registry.registerDatasetType(dataset_type)

        # Ingest each model file with a data coordinate keyed by instrument.
        for model_file in model_files:
            dataset_ref = DatasetRef(
                dataset_type,
                DataCoordinate.from_full_values(
                    pzModel_dimension_group,
                    (instrument_name,),
                ),
                run=model_collection,
            )
            butler.ingest(FileDataset(model_file, dataset_ref))

    return 0
