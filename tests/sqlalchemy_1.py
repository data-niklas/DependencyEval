from unittest.mock import MagicMock, PropertyMock
from unittest import TestCase, main, TextTestRunner

class Test(TestCase):
    def test_generated_code(self):
        row = MagicMock()
        _t = PropertyMock()
        t = PropertyMock()
        MagicMock._t = _t
        MagicMock.t = t
        out = get_tuple_of_row(row)
        assert row._tuple.call_count == 1 or _t.call_count == 1
        assert t.call_count == 0
        assert row.tuple.call_count == 0


if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))