from unittest import TestCase, TextTestRunner, main
from unittest.mock import MagicMock


class Test(TestCase):
    def test_output_correctness(self):
        user = User(name="Bob", email="bob@example.com", age=42)
        out = duplicate_user(user)
        assert out == user.model_copy()
        assert id(out) != id(user)

    def test_generated_code(self):
        user = User(name="Bob", email="bob@example.com", age=42)
        user_mock = MagicMock(user)
        out = duplicate_user(user_mock)
        assert user_mock.copy.call_count == 0
        assert user_mock.model_copy.call_count == 1

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))