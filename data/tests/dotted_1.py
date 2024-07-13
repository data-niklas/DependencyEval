from unittest import TestCase, TextTestRunner, main
from unittest.mock import MagicMock


class Test(TestCase):
    def test_output_correctness(self):
        user = DottedDict({
            "name": "Bob",
            "age": 42,
            "email": "bob@example.com",
            "street": {
                "number": 80,
                "name": "Example Str"
            }
        })
        out = get_user_street_name(user)
        assert out == user["street.name"]

    def test_approach_correctness(self):
        user = {
            "name": "Bob",
            "age": 42,
            "email": "bob@example.com",
            "street": {
                "number": 80,
                "name": "Example Str"
            }
        }
        user_mock = MagicMock()
        user_mock.__getitem__.side_effect = DottedDict(user).__getitem__
        out = get_user_street_name(user_mock)
        assert user_mock.__getitem__.call_count == 1
        assert user_mock.__getitem__.call_args.args == ("street.name",)

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))