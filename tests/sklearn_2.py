from unittest.mock import MagicMock
from unittest import TestCase, main, TextTestRunner
from importlib import reload

class Test(TestCase):
    def test_functionality(self):
        import sklearn.preprocessing
        OneHotEncoder = reload(sklearn.preprocessing).OneHotEncoder
        globals()["OneHotEncoder"] = OneHotEncoder
        out = create_polars_compatible_one_hot_encoder()
        assert isinstance(out, OneHotEncoder)
        assert hasattr(out, "_sklearn_output_config")
        assert "transform" in out._sklearn_output_config
        assert out._sklearn_output_config["transform"] == "polars"

    def test_style(self):
        import sklearn.preprocessing
        OneHotEncoder = reload(sklearn.preprocessing).OneHotEncoder
        OneHotEncoder = MagicMock(OneHotEncoder)
        globals()["OneHotEncoder"] = OneHotEncoder
        out = create_polars_compatible_one_hot_encoder()
        assert OneHotEncoder.call_count == 1
        assert OneHotEncoder.call_args == ()
        assert out.set_output.call_count == 1
        assert out.set_output.call_args == ((),{"transform": "polars"})

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))