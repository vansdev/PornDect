# -*- coding: UTF-8 -*-

# map the x-y coordinate to one-dimensional index
import sys


def valid_coord(x, y , width, height):
    if 0 <= x < width and 0 <= y < height:
        return True
    else:
        return False

def x_y2index(x, y , width, height):
    if valid_coord(x, y, width, height):
        return y * width + x
    else:
        raise IndexError

# 下面的函数用来判定是否肤色
def is_skin(pixel):
    r = pixel[0]
    g = pixel[1]
    b = pixel[2]

    rgb_classifier = r > 95 and \
                     g > 40 and g < 100 and \
                     b > 20 and \
                     max([r, g, b]) - min([r, g, b]) > 15 and \
                     abs(r - g) > 15 and \
                     r > g and \
                     r > b

    nr, ng, nb = to_normalized(r, g, b)
    norm_rgb_classifier = nr / ng > 1.185 and \
                          float(r * b) / ((r + g + b) ** 2) > 0.107 and \
                          float(r * g) / ((r + g + b) ** 2) > 0.112

    # HSV 颜色模式下的判定
    h, s, v = to_hsv(r, g, b)
    hsv_classifier = h > 0 and \
                     h < 35 and \
                     s > 0.23 and \
                     s < 0.68

    # YCbCr 颜色模式下的判定
    y, cb, cr = to_ycbcr(r, g, b)
    ycbcr_classifier = 97.5 <= cb <= 142.5 and 134 <= cr <= 176

    # 效果不是很好，还需改公式
    # return rgb_classifier or norm_rgb_classifier or hsv_classifier or ycbcr_classifier
    return ycbcr_classifier

def to_normalized(r, g, b):
    if r == 0:
        r = 0.0001
    if g == 0:
        g = 0.0001
    if b == 0:
        b = 0.0001
    _sum = float(r + g + b)
    return [r / _sum, g / _sum, b / _sum]

def to_ycbcr(r, g, b):
    # 公式来源：
    # http://stackoverflow.com/questions/19459831/rgb-to-ycbcr-conversion-problems
    y = .299*r + .587*g + .114*b
    cb = 128 - 0.168736*r - 0.331364*g + 0.5*b
    cr = 128 + 0.5*r - 0.418688*g - 0.081312*b
    return y, cb, cr

def to_hsv(r, g, b):
    h = 0
    _sum = float(r + g + b)
    _max = float(max([r, g, b]))
    _min = float(min([r, g, b]))
    diff = float(_max - _min)
    if _sum == 0:
        _sum = 0.0001

    if _max == r:
        if diff == 0:
            h = sys.maxsize
        else:
            h = (g - b) / diff
    elif _max == g:
        h = 2 + ((g - r) / diff)
    else:
        h = 4 + ((r - g) / diff)

    h *= 60
    if h < 0:
        h += 360

    return [h, 1.0 - (3.0 * (_min / _sum)), (1.0 / 3.0) * _max]