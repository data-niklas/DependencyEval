from unittest.mock import MagicMock
from unittest import TestCase, main
from importlib import reload

class Test(TestCase):
    def test_generated_code(self):
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
    result = main(exit=False, verbosity=0).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))