from __future__ import absolute_import, unicode_literals


class EffectBase(object):

    def __init__(self, effect, *args, **kwargs):
        self.effect = effect
        self.func_args = args
        self.func_kwargs = kwargs

    def run(self):
        return self.effect(*self.func_args, **self.func_kwargs)


class Call(EffectBase):
    pass


class Put(EffectBase):

    def run(self):
        return self.effect