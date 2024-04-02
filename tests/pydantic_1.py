from unittest.mock import MagicMock
from unittest import TestCase, main, TextTestRunner

class Test(TestCase):
    def test_functionality(self):
        user = User(name="Bob", email="bob@example.com", age=42)
        out = convert_user_to_dict(user)
        assert out == user.model_dump()

    def test_style(self):
        user = User(name="Bob", email="bob@example.com", age=42)
        user_mock = MagicMock(user)
        out = convert_user_to_dict(user_mock)
        assert user_mock.dict.call_count == 0
        assert user_mock.model_dump.call_count == 1

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))