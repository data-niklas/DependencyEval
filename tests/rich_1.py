from unittest.mock import MagicMock
from unittest import TestCase, main

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
    result = main(exit=False, verbosity=0).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))