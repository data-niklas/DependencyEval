from unittest.mock import MagicMock
from unittest import TestCase, main, TextTestRunner

class Test(TestCase):
    def test_generated_code(self):
        values = bidict({
            "A": "B"
        })
        values = MagicMock(values)
        out = invert_bidict_direction(values)
        assert out == values.inverse
        # TODO: check inverse accessed

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))