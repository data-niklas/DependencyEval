from unittest.mock import MagicMock
from unittest import TestCase, main, TextTestRunner

class Test(TestCase):
    def test_generated_code(self):
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
        assert out == "Example Str"
        assert user_mock.__getitem__.call_count == 1
        assert user_mock.__getitem__.call_args.args == ("street.name",)

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))