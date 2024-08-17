from importlib import reload
from unittest import TestCase, TextTestRunner, main
from unittest.mock import MagicMock

A = ["num", "Hello "]
B = ["py", "World!"]
C = ["numpy", "Hello World!"]

class Test(TestCase):
    def test_output_correctness(self):
        import numpy.strings
        reload(numpy.strings)
        import numpy.char
        reload(numpy.char)
        out = add_strings_element_wise(A, B)
        assert numpy.equal(out, C).all()

    def test_approach_correctness(self):
        import numpy.strings
        reload(numpy.strings)
        import numpy.char
        reload(numpy.char)
        numpy.char.add = MagicMock(numpy.char.add)
        numpy.strings.add = MagicMock(numpy.strings.add)
        out = add_strings_element_wise(A, B)
        assert numpy.char.add.call_count == 0
        assert numpy.strings.add.call_count == 1

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))