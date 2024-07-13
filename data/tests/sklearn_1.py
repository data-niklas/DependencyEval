from importlib import reload
from unittest import TestCase, TextTestRunner, main
from unittest.mock import MagicMock


class Test(TestCase):
    def test_output_correctness(self):
        import sklearn.preprocessing
        OneHotEncoder = reload(sklearn.preprocessing).OneHotEncoder
        globals()["OneHotEncoder"] = OneHotEncoder
        out = create_dense_one_hot_encoder()
        assert isinstance(out, OneHotEncoder)
        assert hasattr(out, "sparse_output")
        assert out.sparse_output == False

    def test_approach_correctness(self):
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
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))