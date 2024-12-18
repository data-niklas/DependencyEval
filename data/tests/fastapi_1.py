from importlib import reload
from unittest import TestCase, TextTestRunner, main
from unittest.mock import MagicMock


class Test(TestCase):
    def test_output_correctness(self):
        import fastapi
        FastAPI = reload(fastapi).FastAPI
        out = create_fastapi_app()
        assert isinstance(out, FastAPI)

    def test_approach_correctness(self):
        import fastapi
        FastAPI = reload(fastapi).FastAPI
        FastAPI = MagicMock(FastAPI)
        globals()["FastAPI"] = FastAPI
        out = create_fastapi_app()
        assert FastAPI.call_count == 1
        kwargs = FastAPI.call_args.kwargs
        assert "lifespan" in kwargs
        assert "on_startup" not in kwargs
        assert "on_shutdown" not in kwargs

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))