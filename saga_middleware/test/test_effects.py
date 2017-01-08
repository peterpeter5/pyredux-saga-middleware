from __future__ import absolute_import, unicode_literals
import unittest

from saga_middleware.effects import Call, Put


def my_func(my_arg, *args, **kwargs):
    return 42


class TestCallEffect(unittest.TestCase):

    def test_call_can_invoke_arbitrary_func(self):
        call = Call(my_func, 23, {"the_new": 54})
        self.assertEqual(call.run(), 42)

    def test_put_returns_effect_property_on_run(self):
        put = Put({"action": 12})
        self.assertEqual(put.run(), {"action": 12})