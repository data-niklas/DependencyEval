from unittest.mock import MagicMock
from unittest import TestCase, main

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
    result = main(exit=False, verbosity=0).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))