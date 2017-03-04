# -*- coding: UTF-8 -*-
# python 3.4
# 用Pillow进行图像处理 简单判别是否有可能是色情图片
# 原理是记录图片中可能是裸露肌肤的区域数目和大小 然后根据一些经验判据决定是否可能是色情图片
# 程序关键在于记录skin_region 即裸露区域的数目和大小  我采用并查集来实现  区别于实验楼的教程  时间复杂度未作比较
# 用多进程对pics文件夹下所有图片进行处理  处理后结果输出到skins文件夹 文件名包含True/False 输出的图片是黑白图 显示皮肤区域
import os
import concurrent.futures
from PIL import Image
from UnionFind import WeightedUnionFind
from tools import x_y2index, is_skin


size_filter = 50

class PornDetect(object):

    def __init__(self, image):
        self._image = image
        self._height = image.height
        self._width = image.width
        self._n = self._height * self._width
        self._UF = WeightedUnionFind(self._n)
        self._skin = []
        self._regions_final = dict() # 存储最终皮肤区域个数和大小  元素形如 root:size

        # 用来计算人体周边矩形面积
        self._skin_x_min = self._width
        self._skin_x_max = -1
        self._skin_y_min = self._height
        self._skin_y_max = -1

    # 预处理
    def pre_process(self):
        bands = self._image.getbands()
        if len(bands) == 1:
            new_img = Image.new('RGB', self._image.size)
            new_img.paste(self._image)
            self._image = new_img

    # 扫描
    def _scan(self):
        pixels = self._image.load()
        for y in range(self._height):
            for x in range(self._width):
                index = x_y2index(x, y, self._width, self._height)

                if is_skin(pixels[x,y]):
                    self._skin.append(True)

                    # 更新矩形区域范围
                    self._skin_x_min = min(self._skin_x_min, x)
                    self._skin_x_max = max(self._skin_x_max, x)
                    self._skin_y_min = min(self._skin_y_min, y)
                    self._skin_y_max = max(self._skin_y_max, y)

                    neighbours = ((-1, 0), (-1, -1), (0, -1), (1, -1))
                    for vec in neighbours:
                        neighbour = (x + vec[0], y + vec[1])
                        try:
                            neighbour_index = x_y2index(neighbour[0], neighbour[1], self._width, self._height)
                        except IndexError:
                            continue
                        if self._skin[neighbour_index]:
                            self._UF.union(index, neighbour_index) # 若本点和邻居都为皮肤 做union操作

                else:
                    self._skin.append(False)

    # 仅保留符合条件的皮肤区域
    def _filter(self):
        for i in range(self._n):
            if self._UF.is_root(i) and self._UF.size(i) >= size_filter:
                self._regions_final[i] = self._UF.size(i)

    # 用self._regions_final 判定是否为色情图片 输出信息
    def _is_porn(self):
        result = True

        if len(self._regions_final) < 3 or len(self._regions_final) > 60:
            result = False
            print('skin regions less than 3 or more than 60.')
        else:
            total_skin_pixels = 0
            for size in self._regions_final.itervalues():
                total_skin_pixels += size
            max_nude_size = max(self._regions_final.itervalues())
            rectangle_size = (self._skin_x_max - self._skin_x_min) * (self._skin_y_max - self._skin_y_min)
            nude_percentage = float(total_skin_pixels) / rectangle_size * 100
            if nude_percentage < 25:
                result = False
                print('total skin region {} is less than 25% of the rectangle around'.format(nude_percentage))
            elif float(max_nude_size) / total_skin_pixels * 100 <45:
                result = False
                print('max skin region {} is less than 45% of total skin region.'.format(float(max_nude_size) / total_skin_pixels * 100))
            else:
                print('it might be porn.')

        return result

    # 调用上述函数 对图片进行处理和判定
    def judge(self):
        self._scan()
        self._filter()
        return self._is_porn()

    # 输出图片相应的黑白图
    def show_skin(self):
        new_img = self._image
        new_img_data = new_img.load()
        for y in range(self._height):
            for x in range(self._width):
                if self._skin[x_y2index(x, y, self._width, self._height)]:
                    new_img_data[x , y] = 0, 0, 0
                else:
                    new_img_data[x , y] = 255, 255, 255

        return new_img

# 多进程的进程工作函数
def worker(filename, src_dir, des_dir):
    image = Image.open(src_dir + filename)
    detector = PornDetect(image)
    result = detector.judge()
    detector.show_skin().save(des_dir + str(result) + '  ' + filename)

# 主函数 多进程处理pics文件夹下所有文件
def main():
    src_dir = './pics/'
    des_dir = './skins/'
    filename_list = os.listdir(src_dir)

    futures = set()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for filename in filename_list:
            future = executor.submit(worker, filename, src_dir, des_dir)
            futures.add(future)

    try:
        for future in concurrent.futures.as_completed(futures):
            err = future.exception()
            if err is not None:
                raise err
    except KeyboardInterrupt:
        print("stopped by hand")


if __name__ == '__main__':
    main()