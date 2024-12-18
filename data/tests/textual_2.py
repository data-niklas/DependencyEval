from importlib import reload
from unittest import TestCase, TextTestRunner, main
from unittest.mock import MagicMock


class Test(TestCase):
    def test_output_correctness(self):
        import textual.widgets
        App = reload(textual.app).App
        globals()["App"] = App
        out = create_app_without_animations()
        assert isinstance(out, App)
        assert hasattr(out, "animation_level")
        assert out.animation_level == "none"

    def test_approach_correctness(self):
        import textual.widgets
        App = reload(textual.app).App
        App = MagicMock(App)
        globals()["App"] = App
        out = create_app_without_animations()
        assert App.call_count == 1
        assert App.call_args == ()
        assert out.animation_level == "none"

if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)
    import json
    import os
    result = main(exit=False, verbosity=0, testRunner=TextTestRunner(verbosity=0, stream=open(os.devnull,"w"))).result
    print(json.dumps([len(result.errors), len(result.failures), result.testsRun]))