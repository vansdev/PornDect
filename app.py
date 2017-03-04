# -*- coding: UTF-8 -*-
from UnionFind import WeightedUnionFind
from tools import x_y2index, is_skin
class PornDetect(object):

    def __init__(self, image):
        self._image = image
        self._height = 0
        self._width = 0
        self._n = self._height * self._width
        self._UF = WeightedUnionFind(self._n)
        self._skin = []

    def scan(self):
        for y in range(self._height):
            for x in range(self._width):
                index = x_y2index(x, y)


    def filter(self):
        pass


    def is_porn(self, nude_regions):
        return False


def main():
    image = None
    detector = PornDetect(image)
    print(detector.is_porn())

if __name__ == '__main__':
    main()