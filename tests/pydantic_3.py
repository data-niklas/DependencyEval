from unittest.mock import MagicMock
from unittest import TestCase, main

class Test(TestCase):
    def test_generated_code(self):
        user = User(name="Bob", email="bob@example.com", age=42)
        user_mock = MagicMock(user)
        out = duplicate_user(user_mock)
        assert user_mock.copy.call_count == 0
        assert user_mock.model_copy.call_count == 1
        out = duplicate_user(user)
        assert out == user.model_copy()
        assert id(out) != id(user)

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    result = main(exit=False, verbosity=0).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))