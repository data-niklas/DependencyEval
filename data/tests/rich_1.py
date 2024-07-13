from unittest import TestCase, TextTestRunner, main
from unittest.mock import MagicMock


class Test(TestCase):
    def test_output_correctness(self):
        style = Style()
        out = clear_style(style)
        assert out == style.clear_meta_and_links()

    def test_approach_correctness(self):
        style = Style()
        style_mock = MagicMock(style)
        out = clear_style(style_mock)
        assert style_mock.clear_meta_and_links.call_count == 1
        assert style_mock.clear_meta_and_links.call_args == ()

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))