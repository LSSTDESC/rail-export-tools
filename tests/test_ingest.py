from lsst.daf.butler import CollectionType

from rail_export.butler_ingest_models import ingest_models
from rail_export.ingest import ingest


def _register_run(butler, run_name):
    butler.registry.registerCollection(run_name, CollectionType.RUN)


class TestIngestModels:

    def test_registers_dataset_type(self, butler):
        _register_run(butler, "test/models")
        models = {"knn": ["/fake/model_knn.pkl"]}

        ingest_models(butler, "test/models", models, instrument_name="LSSTCam")

        dataset_type = butler.registry.getDatasetType("pzModel_knn")
        assert dataset_type is not None
        assert dataset_type.name == "pzModel_knn"
        assert dataset_type.storageClass_name == "PZModel"

    def test_calls_ingest_for_each_file(self, butler):
        _register_run(butler, "test/models")
        models = {
            "knn": ["/fake/model_knn.pkl"],
            "bpz": ["/fake/model_bpz.pkl"],
        }

        ingest_models(butler, "test/models", models, instrument_name="LSSTCam")

        assert butler._datastore.ingest.call_count == 2

    def test_multiple_algos(self, butler):
        _register_run(butler, "test/models")
        models = {
            "knn": ["/fake/model_knn.pkl"],
            "bpz": ["/fake/model_bpz.pkl"],
        }

        result = ingest_models(butler, "test/models", models, instrument_name="LSSTCam")

        assert result == 0
        assert butler.registry.getDatasetType("pzModel_knn") is not None
        assert butler.registry.getDatasetType("pzModel_bpz") is not None
        assert butler._datastore.ingest.call_count == 2

    def test_reuses_existing_dataset_type(self, butler):
        _register_run(butler, "test/models")
        _register_run(butler, "test/models2")
        models = {"knn": ["/fake/model_knn.pkl"]}

        ingest_models(butler, "test/models", models, instrument_name="LSSTCam")
        ingest_models(butler, "test/models2", models, instrument_name="LSSTCam")

        dataset_type = butler.registry.getDatasetType("pzModel_knn")
        assert dataset_type is not None

    def test_returns_zero(self, butler):
        _register_run(butler, "test/models")
        models = {"knn": ["/fake/model_knn.pkl"]}

        result = ingest_models(butler, "test/models", models, instrument_name="LSSTCam")

        assert result == 0


class TestIngest:

    def test_builds_correct_paths(self, butler, model_files):
        model_dir_parent, algos, _ = model_files
        _register_run(butler, "pretrained/pz/v2/gold/dp1_6band")

        result = ingest(
            butler,
            algos=algos,
            model_base_dir=str(model_dir_parent.parent),
            model_base_col="pretrained/pz",
            version="v2",
            flavor="dp1_6band",
            selection="gold",
            instrument_name="LSSTCam",
        )

        assert result == 0
        for algo in algos:
            dataset_type = butler.registry.getDatasetType(f"pzModel_{algo}")
            assert dataset_type is not None

    def test_no_files_found(self, butler, tmp_path):
        model_dir = tmp_path / "models_v1_empty"
        model_dir.mkdir()
        _register_run(butler, "pretrained/pz/v1/gold/empty")

        result = ingest(
            butler,
            algos=["knn"],
            model_base_dir=str(tmp_path),
            model_base_col="pretrained/pz",
            version="v1",
            flavor="empty",
            instrument_name="LSSTCam",
        )

        assert result == 0
        assert butler._datastore.ingest.call_count == 0

    def test_ingest_with_comcam(self, butler, model_files):
        model_dir_parent, algos, _ = model_files
        _register_run(butler, "pretrained/pz/v2/gold/dp1_6band")

        result = ingest(
            butler,
            algos=algos,
            model_base_dir=str(model_dir_parent.parent),
            model_base_col="pretrained/pz",
            version="v2",
            flavor="dp1_6band",
            instrument_name="LSSTComCam",
        )

        assert result == 0
