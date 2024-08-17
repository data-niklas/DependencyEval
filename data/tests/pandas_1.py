from unittest import TestCase, TextTestRunner, main
from unittest.mock import MagicMock
import io
CSV_DATA = '''Last Name,First Name,Age,Country
?,?,?,UK
Davis,Michael,42,UK
'''

class Test(TestCase):
    def create_df(self):
        return pd.read_csv(io.StringIO(CSV_DATA), na_values="?")

    def test_output_correctness(self):
        df = self.create_df()
        grouped_df = df.groupby('Country')
        out = get_first_group_entry_allow_na(grouped_df)
        assert out.equals(grouped_df.first(skipna=False))

    def test_approach_correctness(self):
        df = self.create_df()
        grouped_df = df.groupby('Country')
        grouped_df_mock = MagicMock(grouped_df)
        out = get_first_group_entry_allow_na(grouped_df_mock)
        assert grouped_df_mock.first.call_count == 1
        kwargs = grouped_df_mock.first.call_args.kwargs
        assert "skipna" in kwargs, json.dumps(kwargs)
        assert kwargs["skipna"] == False

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))