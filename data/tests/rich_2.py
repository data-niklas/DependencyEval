from unittest import TestCase, TextTestRunner, main
from unittest.mock import MagicMock


class Test(TestCase):
    def test_output_correctness(self):
        text = "This is a test"
        prompt = create_case_insensitive_prompt(text)
        assert prompt.case_sensitive == False
        assert prompt.prompt._text[0] == text

    def test_approach_correctness(self):
        global Prompt
        oldPrompt = Prompt
        Prompt = MagicMock(Prompt)
        text = "This is a test"
        prompt = create_case_insensitive_prompt(text)
        assert Prompt.call_count == 1
        kwargs = Prompt.call_args.kwargs
        assert "case_sensitive" in kwargs
        assert kwargs["case_sensitive"] == False
        Prompt = oldPrompt

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))