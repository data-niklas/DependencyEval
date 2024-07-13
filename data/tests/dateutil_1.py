from datetime import timedelta
from unittest import TestCase, TextTestRunner, main
from unittest.mock import MagicMock, PropertyMock


class Test(TestCase):
    def test_output_correctness(self):
        expected_current_date = datetime.now(dateutil.tz.tzlocal())
        actual_current_date = current_datetime_in_local_timezone()
        assert actual_current_date - expected_current_date < timedelta(seconds=1)

    def test_approach_correctness(self):
        current_date = current_datetime_in_local_timezone()
        assert isinstance(current_date, datetime)
        assert current_date.tzinfo == dateutil.tz.tzlocal()

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))