from unittest.mock import MagicMock
from unittest import TestCase, main, TextTestRunner

class Test(TestCase):
    def test_functionality(self):
        values = bidict({
            "A": "B"
        })
        values2 = values.copy()
        items = {
            "A": "C",
            "D": "E"
        }
        insert_values_drop_old_on_dup(values, items)
        values2.putall(items, OnDup(key=OnDupAction.DROP_OLD, val=OnDupAction.DROP_OLD))
        assert values == values2

    def test_style(self):
        values = bidict({
            "A": "B"
        })
        items = {
            "A": "C",
            "D": "E"
        }
        values = MagicMock(values)
        insert_values_drop_old_on_dup(values, items)
        assert values.putall.call_count == 1
        args = values.putall.call_args.args
        kwargs = values.putall.call_args.kwargs
        assert (len(args) > 0 and args[0] == items) or kwargs["items"] == items
        dup = args[1] if len(args) == 2 else kwargs["on_dup"]
        assert dup == OnDup(key=OnDupAction.DROP_OLD, val=OnDupAction.DROP_OLD)


if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))