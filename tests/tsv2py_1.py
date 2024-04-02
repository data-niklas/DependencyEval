from unittest.mock import MagicMock
from unittest import TestCase, main, TextTestRunner
import os

class Test(TestCase):
    def test_functionality(self):
        people = [
            ("Bob", 42, datetime.now()),
            ("Marta", 70, datetime.now()),
            ("Lukas", 51, datetime.now()),
            ("Elsa", 3, datetime.now()),
        ]
        file = "__tsv2py_1__.csv"
        with open(file, "w") as f:
            f.write("\n".join([
                "{}\t{}\t{}".format(p[0], p[1], p[2].strftime("%Y-%m-%dT%H:%M:%SZ"))
                for p in people
            ]))
        try:
            result = parse_tsv_file(file)
            assert len(people) == len(result)
            for p1, p2 in zip(people, result):
                assert p1[0] == p2[0]
                assert p1[1] == p2[1]
        except:
            assert False
        finally:
            os.remove(file)

    def test_style(self):
        self.test_functionality()
        # TODO: properly mock objects

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))