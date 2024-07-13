from unittest import TestCase, TextTestRunner, main
from unittest.mock import MagicMock


class Test(TestCase):
    def test_output_correctness(self):
        start = 11
        end = 23
        out = create_1d_tensor_in_range(start, end)
        assert torch.equal(out, torch.arange(start, end))

    def test_approach_correctness(self):
        torch.arange = MagicMock(torch.arange)
        torch.range = MagicMock(torch.range)
        start = 11
        end = 23
        out = create_1d_tensor_in_range(start, end)
        assert torch.arange.call_count == 1
        assert torch.range.call_count == 0

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))