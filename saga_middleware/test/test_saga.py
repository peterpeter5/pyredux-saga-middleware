from __future__ import absolute_import, unicode_literals, generators
import unittest
from pyredux.Actions import create_typed_action_creator

from saga_middleware.effects import Call, Put
from saga_middleware.saga import Trampoline, Saga

Action, creator = create_typed_action_creator("A_Action")


def my_saga(action):
    pass


def get_answer(guess=None):
    if guess is None:
        return 42
    else:
        raise ValueError("Wrong guess")


def call_saga(action):
    print(action)
    first_answer = yield Call(get_answer)
    second_answer = yield Call(get_answer)
    third_answer = yield Call(get_answer)
    yield first_answer + second_answer + third_answer


def exception_saga(action):
    try:
        error = yield Call(get_answer, 23)
    except ValueError as error:
        error = "error thrown"
        yield error
    additional_info = yield Call(get_answer)
    yield error + str(additional_info)


def put_saga(action):
    payload = yield Call(get_answer)
    add_payload = creator(payload)
    yield Put(add_payload)


class StoreMock(object):

    def __init__(self):
        self.state = list()

    def dispatch(self, action):
        self.state.append(action)


class TestSagaRunner(unittest.TestCase):

    def test_trampoline_can_run_saga_with_many_call_effects(self):
        trample = Trampoline()
        trample.register_saga({Action: call_saga})
        result = trample.run(creator())
        self.assertEqual(result, 3*get_answer())

    def test_trampoline_will_throw_exceptions_in_saga_context(self):
        trample = Trampoline()
        trample.register_saga({Action: exception_saga})
        result = trample.run(creator())
        self.assertEqual(result, "error thrown42")

    def test_trampoline_will_dispatch_put_effects(self):
        store = StoreMock()
        trample = Trampoline()
        trample.register_store(store)
        trample.register_saga({Action: put_saga})
        trample.run(creator())
        self.assertEqual(len(store.state), 1)
        self.assertEqual(store.state[0].payload, 42)


class TestTakeEvery(unittest.TestCase):

    def test_take_every_add_action_and_funcs_to_dispatcher(self):
        saga = Saga()
        saga.take_every(Action, my_saga)
        self.assertEqual(saga._trampoline.dispatcher, {Action: my_saga})