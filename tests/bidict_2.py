from unittest.mock import MagicMock, PropertyMock
from unittest import TestCase, main, TextTestRunner

class Test(TestCase):
    def test_output_correctness(self):
        values = bidict({
            "A": "B"
        })
        out = invert_bidict_direction(values)
        assert out == values.inverse

    def test_approach_correctness(self):
        values = bidict({
            "A": "B"
        })
        p = PropertyMock()
        values = MagicMock(values)
        type(values).inverse = p
        out = invert_bidict_direction(values)
        p.assert_called_once_with()
        # TODO: check inverse accessed

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))