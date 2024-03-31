from unittest.mock import MagicMock
from unittest import TestCase, main, TextTestRunner

class Test(TestCase):
    def test_generated_code(self):
        style = Style()
        style_mock = MagicMock(style)
        out = clear_style(style_mock)
        assert clear_style(style) == style.clear_meta_and_links()
        assert style_mock.clear_meta_and_links.call_count == 1
        assert style_mock.clear_meta_and_links.call_args == ()

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))