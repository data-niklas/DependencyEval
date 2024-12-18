import os
from unittest import TestCase, TextTestRunner, main
from unittest.mock import MagicMock


class Test(TestCase):
    def test_output_correctness(self):
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

    def test_approach_correctness(self):
        # TODO: mock file opening and other functions
        self.test_output_correctness()

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))