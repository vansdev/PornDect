# -*- coding: UTF-8 -*-

class WeightedUnionFind(object):

    def __init__(self, n):
        self._id = [i for i in range(n)]
        self._size = [1 for i in range(n)]

    def union(self, p, q):
        pass

    def connected(self, p, q):
        pass

    def _root(self, p):
        pass

    def is_root(self, p):
        return False

    def size(self, p):
        return 1