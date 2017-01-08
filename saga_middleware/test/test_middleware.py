from __future__ import absolute_import, unicode_literals

import unittest

from pyredux import apply_middleware
from pyredux import create_store
from pyredux import create_typed_action_creator
from pyrsistent import pmap
from pyrsistent import pvector

from saga_middleware.effects import Call, Put
from saga_middleware.saga import Saga

Todo, create_add_todo = create_typed_action_creator("ADD_TODO")
AsyncTodo, fetch_async_creator = create_typed_action_creator("ASYNC_ACTION")
AsyncFail, failed_fetch = create_typed_action_creator("ASYNC_ERROR")


def action_logger(action, state=pmap({"actions": pvector()})):
    if isinstance(action, Todo) or isinstance(action, AsyncTodo) or isinstance(action, AsyncFail):
        new_actions = state["actions"].append(action)
        return state.update({"actions": new_actions})
    else:
        return state


def get_answer(guess=None):
    if guess is not None:
        raise ValueError("Wrong guess")
    return 42

saga_runned = False


def my_saga_fetcher(action):
    global saga_runned
    saga_runned = True
    try:
        result = yield Call(get_answer, action.payload)
        store_result = str(action.payload) + str(result)
        yield Put(create_add_todo(store_result))
    except ValueError as error:
        yield Put(failed_fetch(error))


class TestSagaMiddleware(unittest.TestCase):
    def test_can_apply_saga_middleware(self):
        saga = Saga()
        store = create_store(action_logger, enhancer=apply_middleware(saga.saga_middleware))
        self.assertIsNotNone(store)

    def test_only_resolved_saga_actions_are_dispatched(self):
        saga = Saga()
        saga.take_every(AsyncTodo, my_saga_fetcher)
        store = create_store(action_logger, enhancer=apply_middleware(saga.saga_middleware))
        store.dispatch(fetch_async_creator())
        new_state = store.state
        actions_ = new_state["actions"]
        self.assertEqual(len(actions_), 1)
        self.assertIsInstance(actions_[0], Todo)
        self.assertEqual(actions_[0].payload, "None42")
        self.assertTrue(saga_runned)

    def test_non_saga_actions_get_passed_to_the_store(self):
        global saga_runned
        saga_runned = False
        saga = Saga()
        saga.take_every(AsyncTodo, my_saga_fetcher)
        store = create_store(action_logger, enhancer=apply_middleware(saga.saga_middleware))
        store.dispatch(create_add_todo("Learn fancy"))
        self.assertEqual(len(store.state["actions"]), 1)
        self.assertIsInstance(store.state["actions"][0], Todo)
        self.assertFalse(saga_runned)

    def test_exception_handling_works_properly(self):
        global saga_runned
        saga_runned = False
        saga = Saga()
        saga.take_every(AsyncTodo, my_saga_fetcher)
        store = create_store(action_logger, enhancer=apply_middleware(saga.saga_middleware))
        store.dispatch(fetch_async_creator("this_is_failing"))
        self.assertEqual(len(store.state["actions"]), 1)
        self.assertIsInstance(store.state["actions"][0], AsyncFail)
        self.assertTrue(saga_runned)