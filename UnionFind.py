# -*- coding: UTF-8 -*-
# 带权并查集的python实现
# 参见 Robert Sedgewick 的算法书
class WeightedUnionFind(object):

    def __init__(self, n):
        self._parent = [i for i in range(n)]
        self._size = [1 for i in range(n)]

    def union(self, p, q):
        if self.connected(p, q):
            pass
        else:
            root_p = self._root(p)
            root_q = self._root(q)
            if self._size[root_p] < self._size[root_q]:
                self._parent[root_p] = root_q
                self._size[root_q] += self._size[root_p]
            else:
                self._parent[root_q] = root_p
                self._size[root_p] += self._size[root_q]

    def connected(self, p, q):
        return self._root(p) == self._root(q)

    def _root(self, p):
        while self._parent[p] != p:
            p = self._parent[p]
        return p

    def is_root(self, p):
        return p == self._parent[p]

    def size(self, p):
        return self._size[p]