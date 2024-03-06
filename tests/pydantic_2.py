from unittest.mock import MagicMock
from unittest import TestCase, main

class Test(TestCase):
    def test_generated_code(self):
        user = User(name="Bob", email="bob@example.com", age=42)
        user_mock = MagicMock(user)
        out = convert_user_to_json(user_mock)
        assert user_mock.json.call_count == 0
        assert user_mock.model_dump_json.call_count == 1
        out = convert_user_to_json(user)
        assert out == user.model_dump_json()

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    result = main(exit=False, verbosity=0).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))