from unittest.mock import MagicMock
from unittest import TestCase, main

class Test(TestCase):
    def test_generated_code(self):
        torch.cholesky = MagicMock(torch.cholesky)
        torch.linalg.cholesky = MagicMock(torch.linalg.cholesky)
        tensor = torch.Tensor()
        out = calculate_cholesky(tensor)
        assert torch.cholesky.call_count == 0
        assert torch.linalg.cholesky.call_count == 1

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    result = main(exit=False, verbosity=0).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))