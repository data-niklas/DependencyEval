from unittest.mock import MagicMock
from unittest import TestCase, main, TextTestRunner, TextTestRunner
from importlib import reload

class Test(TestCase):
    def test_generated_code(self):
        import torch.nn
        CrossEntropyLoss = reload(torch.nn).CrossEntropyLoss
        CrossEntropyLoss = MagicMock(CrossEntropyLoss)
        globals()["CrossEntropyLoss"] = CrossEntropyLoss
        out = create_sum_cross_entropy_loss_module()
        assert CrossEntropyLoss.call_count == 1
        kwargs = CrossEntropyLoss.call_args.kwargs
        assert "reduction" in kwargs
        assert "reduce" not in kwargs
        assert "size_average" not in kwargs

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))