import pytest

from lsst.daf.butler import StorageClass, StorageClassFactory
from lsst.daf.butler.tests import makeTestRepo, DatastoreMock


@pytest.fixture
def butler(tmp_path):
    factory = StorageClassFactory()
    try:
        factory.getStorageClass("PZModel")
    except KeyError:
        factory.registerStorageClass(StorageClass("PZModel", pytype=dict))

    b = makeTestRepo(
        str(tmp_path / "repo"),
        dataIds={"instrument": ["LSSTCam", "LSSTComCam"]},
    )
    DatastoreMock.apply(b)
    yield b
    b.close()


@pytest.fixture
def model_files(tmp_path):
    model_dir = tmp_path / "models_v2_dp1_6band"
    model_dir.mkdir()

    algos = ["knn", "bpz", "fzboost"]
    paths = []
    for algo in algos:
        p = model_dir / f"trained_{algo}_model.pkl"
        p.write_bytes(b"fake model data")
        paths.append(p)

    return model_dir, algos, paths
