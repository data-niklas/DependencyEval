from unittest.mock import MagicMock
from unittest import TestCase, main
import os

class Test(TestCase):
    def test_generated_code(self):
        file = "__polars_1__.csv"
        with open(file, "w") as f:
            f.write("name,age\nBob,42\nMarta,70\nLukas,51\nElsa,3")
        try:
            result = lazy_filter_old_users(file)
            assert result == ["Marta", "Lukas"]
        except:
            assert False
        finally:
            os.remove(file)

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    result = main(exit=False, verbosity=0).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))