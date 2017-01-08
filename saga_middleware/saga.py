from __future__ import absolute_import, unicode_literals, generators
from saga_middleware.effects import Put, Call, EffectBase


class AlreadyConfigureError(Exception):
    pass


class Trampoline(object):

    def __init__(self):
        self.store = None
        self.dispatcher = dict()

    def register_store(self, store):
        if self.store is not None:
            raise AlreadyConfigureError(
                "Trampoline has already a registered store. Its not allowed to re-register a store!"
            )
        self.store = store

    def register_saga(self, saga):
        self.dispatcher.update(saga)

    def run(self, action):
        if type(action) not in self.dispatcher:
            return action
        result = None
        saga_for_action = self.dispatcher[type(action)](action)
        next_step = saga_for_action.send
        while True:
            try:
                effect = next_step(result)
            except StopIteration:
                break

            result, error = self.execute_effect(effect, saga_for_action)
            if error is not None:
                next_step = saga_for_action.throw
                result = error
            else:
                next_step = saga_for_action.send

            if isinstance(effect, Put):
                result = self.store.dispatch(result)

        return result

    def execute_effect(self, effect, saga_for_action):
        error = None
        if isinstance(effect, EffectBase):
            try:
                result = effect.run()
            except Exception as _error:
                result = None
                error = _error
        else:
            result = effect
        return result, error


class Saga(object):
    def __init__(self):
        self._trampoline = Trampoline()

    def saga_middleware(self, store):
        self._trampoline.register_store(store)

        def _next_wrapper(next_middleware):
            def _middleware(action):
                handle_action = self._trampoline.run(action)
                if handle_action is action:
                    return next_middleware(action)
            return _middleware
        return _next_wrapper

    def take_every(self, action, funcs):
        self._trampoline.register_saga({action: funcs})