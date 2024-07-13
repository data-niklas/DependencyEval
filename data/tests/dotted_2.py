from unittest import TestCase, TextTestRunner, main
from unittest.mock import MagicMock


class Test(TestCase):
    def test_output_correctness(self):
        board = DottedList([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        out = get_2d_board_entry(board, "1.2")
        assert out == board["1.2"]

    def test_approach_correctness(self):
        board = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        board_mock = MagicMock()
        board_mock.__getitem__.side_effect = DottedList(board).__getitem__
        out = get_2d_board_entry(board_mock, "1.2")
        assert board_mock.__getitem__.call_count == 1
        assert board_mock.__getitem__.call_args.args == ("1.2",)

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))