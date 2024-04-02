from unittest.mock import MagicMock
from unittest import TestCase, main, TextTestRunner

class Test(TestCase):
    def test_functionality(self):
        tensor = torch.Tensor([[1,0],[0,1]])
        out = calculate_cholesky(tensor)
        assert torch.equal(out, torch.linalg.cholesky(tensor))

    def test_style(self):
        torch.cholesky = MagicMock(torch.cholesky)
        torch.linalg.cholesky = MagicMock(torch.linalg.cholesky)
        tensor = torch.Tensor([[1,0],[0,1]])
        out = calculate_cholesky(tensor)
        assert torch.cholesky.call_count == 0
        assert torch.linalg.cholesky.call_count == 1

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))