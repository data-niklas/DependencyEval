from unittest.mock import MagicMock
from unittest import TestCase, main, TextTestRunner

class Test(TestCase):
    def test_output_correctness(self):
        assert multiply_then_square(1, 3) == 9
        assert multiply_then_square(2, 2) == 16

    def test_approach_correctness(self):
        msf = MultiplySquareFlow
        mb = MultiplyBy
        try:
            globals()["MultiplySquareFlow"] = MagicMock(msf)
            globals()["MultiplyBy"] = MagicMock(mb)
            multiply_then_square(1, 3)

            assert MultiplySquareFlow.call_count == 1
            assert MultiplyBy.call_count == 1
            assert MultiplyBy.call_args == ((),{"factor":3})
            assert "square" in MultiplySquareFlow.call_args.kwargs
            assert MultiplySquareFlow.call_args.kwargs["square"] == square
        finally:
            globals()["MultiplySquareFlow"] = msf
            globals()["MultiplyBy"] = mb




if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))