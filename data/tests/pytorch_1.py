from unittest.mock import MagicMock
from unittest import TestCase, main, TextTestRunner, TextTestRunner

class Test(TestCase):
    def test_output_correctness(self):
        out = create_sum_cross_entropy_loss_module()
        assert isinstance(out, CrossEntropyLoss)
        try:
            assert out.reduction == "sum"
        except AttributeError:
            assert False

    def test_approach_correctness(self):
        global CrossEntropyLoss
        oldCrossEntropyLoss = CrossEntropyLoss
        CrossEntropyLoss = MagicMock(CrossEntropyLoss)
        out = create_sum_cross_entropy_loss_module()
        assert CrossEntropyLoss.call_count == 1
        kwargs = CrossEntropyLoss.call_args.kwargs
        assert "reduction" in kwargs
        assert "reduce" not in kwargs
        assert "size_average" not in kwargs
        CrossEntropyLoss = oldCrossEntropyLoss

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))