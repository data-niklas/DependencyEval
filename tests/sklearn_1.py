from unittest.mock import MagicMock
from unittest import TestCase, main
from importlib import reload

class Test(TestCase):
    def test_generated_code(self):
        import sklearn.preprocessing
        OneHotEncoder = reload(sklearn.preprocessing).OneHotEncoder
        OneHotEncoder = MagicMock(OneHotEncoder)
        globals()["OneHotEncoder"] = OneHotEncoder
        out = create_dense_one_hot_encoder()
        assert OneHotEncoder.call_count == 1
        kwargs = OneHotEncoder.call_args.kwargs
        assert "sparse_output" in kwargs
        assert "sparse" not in kwargs
        assert kwargs["sparse_output"] == False

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    result = main(exit=False, verbosity=0).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))