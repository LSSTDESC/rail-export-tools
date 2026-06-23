from pathlib import Path

from lsst.daf.butler import (
    Butler,
    DataCoordinate,
    DatasetRef,
    DatasetType,
    DimensionGroup,
    DimensionUniverse,
    FileDataset,
)


dim_universe = DimensionUniverse()

pzModel_dimension_group = DimensionGroup(
    dim_universe,
    ["instrument"],
)


def ingest_models(
    butler: Butler,
    model_collection: str,
    models: dict[str, list[str | Path]],
    instrument_name: str = "LSSTCam",
) -> int:

    for algo_, model_files in models.items():
        model_type = f"pzModel_{algo_}"
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
