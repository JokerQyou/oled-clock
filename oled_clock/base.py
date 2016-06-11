# -*- coding: utf-8 -*-

class Object(dict):
    def __init__(self, d):
        super(Object, self).__init__()
        self.update(d)

    def __setattr__(self, name, value):
        self[name] = value

    def __getattr__(self, name):
        return self[name]
