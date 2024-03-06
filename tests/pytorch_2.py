from unittest.mock import MagicMock
from unittest import TestCase, main

class Test(TestCase):
    def test_generated_code(self):
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
    result = main(exit=False, verbosity=0).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))