from importlib import reload
from unittest import TestCase, TextTestRunner, main
from unittest.mock import MagicMock


class Test(TestCase):
    def test_output_correctness(self):
        reload(emoji)
        assert does_the_text_contain_only_emojis("👍👍👍") == THUMBS_UP
        assert does_the_text_contain_only_emojis("no") == THUMBS_DOWN

    def test_approach_correctness(self):
        reload(emoji)
        purely_emoji = MagicMock(emoji.purely_emoji)
        emoji.purely_emoji = purely_emoji
        function_input = "👍👍👍"
        does_the_text_contain_only_emojis(function_input)

        items = (function_input,)
        assert purely_emoji.call_count == 1



if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))