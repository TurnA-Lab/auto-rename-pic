#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'iskye'

import os
import re
import string
from shutil import copyfile
from typing import List

import beeprint
import cv2
import numpy
from cnocr import CnOcr
from cnstd import CnStd
from tqdm import tqdm


class PickStuNumber:
    def __init__(self, path: str, show_img: bool = False):
        self.__ext = {'jpg', 'jpeg'}
        self.__ocr = CnOcr(model_name='densenet-lite-gru', cand_alphabet=string.digits, name=path)
        self.__std = CnStd(name=path)
        self.__info_dict = {}
        self.__dup_name_dict = {}

        # 先对路径进行替换
        path = self.__format_path(path)

        # 根据传入的路径判断操作
        if os.path.isdir(path) or os.path.isfile(path):
            files = [self.__format_path(os.path.join(path, f)) for f in os.listdir(path) if
                     (os.path.isfile(os.path.join(path, f)) and self.__is_image(f))] \
                if os.path.isdir(path) \
                else [path]
            for file in tqdm(files):
                self.__handle_info(file,
                                   self.__ocr_number(self.__std_number(self.__cutter(file, show_img))))
        else:
            print(f'获取数据错误，“{path}”既不是文件也不是文件夹')

    @staticmethod
    def __format_path(path: str):
        return os.path.abspath(path).replace('\\', '/')

    @staticmethod
    def __get_suffix(path: str) -> str:
        """
        获取后缀
        :param path: 图片路径
        :return: 是否为图片
        """
        return path.split('.')[-1]

    def __is_image(self, path: str) -> bool:
        return self.__get_suffix(path) in self.__ext

    @staticmethod
    def __cutter(path: str, show_img: bool = False) -> numpy.ndarray:
        """
        切割图片
        :param path: 图片路径
        :param show_img: 是否需要展示图片
        :return: 图片对应的 ndarray
        """
        print(path)

        # 以灰度模式读取图片
        origin_img = cv2.imread(path, 0)

        if show_img:
            # 自由拉伸窗口
            # cv2.namedWindow('bin img', 0)
            cv2.imshow('origin img', origin_img)

        # 切出一部分，取值是经验值
        origin_img = origin_img[:origin_img.shape[0] // 2]

        # 二值化
        _, origin_img = cv2.threshold(origin_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        if show_img:
            # 自由拉伸窗口
            # cv2.namedWindow('bin img', 0)
            cv2.imshow('bin img', origin_img)

        # 形态学转换，主要为了检测出那个红色的 banner
        kernel = numpy.ones((15, 15), dtype=numpy.uint8)
        # img = cv2.erode(img, kernel=kernel, iterations=1)
        img = cv2.dilate(origin_img, kernel=kernel, iterations=2)

        # 边缘检测
        contours, _ = cv2.findContours(img, 1, 2)
        # 找出第二大的，即红色的 banner
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        if len(contours) > 1:
            # 获取包围 banner 的矩形数据
            x, y, w, h = cv2.boundingRect(contours[1])

            # 目前所有的数值设定使用的是经验值
            if w * h > 250000:
                # 需要识别的学号部分
                # 左上角坐标
                left_top_x = x
                left_top_y = y + h + 20
                # 右下角坐标
                right_down_x = x + w
                right_down_y = y + h + 190

                img = origin_img[left_top_y:right_down_y, left_top_x:right_down_x]
            else:
                img = origin_img[120:]
        else:
            img = origin_img[120:]

        # 对切出的图片进行再次处理，以便图像识别
        kernel = numpy.ones((2, 2), dtype=numpy.uint8)
        # 腐蚀以加粗
        img = cv2.erode(img, kernel=kernel, iterations=1)
        # 重新映射回 rgb
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

        if show_img:
            # 自由拉伸窗口
            # cv2.namedWindow('final img', 0)
            cv2.imshow('final img', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return img

    def __ocr_number(self, img_list: List[numpy.ndarray]):
        """
        识别数字
        :param img_list:
        :return:
        """
        return self.__ocr.ocr_for_single_lines(img_list)

    def __std_number(self, img: numpy.ndarray):
        """
        定位数字
        :param img:
        :return:
        """
        return [i['cropped_img'] for i in self.__std.detect(img)]

    @staticmethod
    def __handle_result_list(result_list: List[List[str]]) -> [str, bool]:
        """
        处理结果列表
        :param result_list: 结果列表
        :return: 结果，是否有效
        """
        result = result_list[0]

        if len(result) < 12 and len(result_list) > 1:
            for i in result_list:
                if len(i) >= 12:
                    result = i

        result = ''.join(result[:12] if len(result) >= 12 else result)
        print(result, re.match(r'\d{12}', result) is not None)
        return result, re.match(r'\d{12}', result) is not None

    def __handle_dup_name(self, name, path):
        dup_keys = self.__dup_name_dict.get(name)
        # 如设置过，即表明有重复的
        if dup_keys:
            # 设置重复的为 True，只要第一次重复时设置即可
            if 1 == len(dup_keys):
                self.__info_dict[dup_keys[0]]['dup'] = True
            # 将本次的 path 也添加进去
            self.__dup_name_dict[name].append(path)
            return True
        else:
            self.__dup_name_dict[name] = [path]
            return False

    def __handle_info(self, key, value):
        """
        处理每条信息
        :param key:
        :param value:
        """
        name, is_legal = self.__handle_result_list(value)
        self.__info_dict[key] = {
            'name': name,
            'suffix': self.__get_suffix(key),
            'legal': is_legal,
            'dup': self.__handle_dup_name(name, key)
        }

    def print_info(self):
        """
        打印图片信息
        :return:
        """
        beeprint.pp(self.__info_dict)
        return self

    def print_dup(self):
        """
        打印重复图片信息
        :return:
        """
        beeprint.pp(self.__dup_name_dict)
        return self

    def write_out(self,
                  path: str = '.',
                  out_path_suc: str = 'output_suc',
                  out_path_dup: str = 'output_dup',
                  out_path_fail: str = 'output_fail'):
        """
        输出重命名后的图片到文件夹
        :param path: 文件夹路径
        :param out_path_suc: 合规且不重复图片所在的文件夹
        :param out_path_dup: 合规但是重复图片所在的文件夹
        :param out_path_fail: 其它图片所在文件夹
        :return: self
        """
        # 处理路径
        path = self.__format_path(path)

        if os.path.isdir(path):
            # 拼接文件路径
            suc = os.path.join(path, out_path_suc)
            fail = os.path.join(path, out_path_fail)
            dup = os.path.join(path, out_path_dup)

            #  创建结果文件夹
            not os.path.exists(suc) and os.makedirs(suc)
            not os.path.exists(fail) and os.makedirs(fail)
            not os.path.exists(dup) and os.makedirs(dup)

            # 将图片输出到相应的文件夹
            for key, value in self.__info_dict.items():
                # 合规且不重复
                if value.get('legal') is True and value.get('dup') is False:
                    copyfile(key, os.path.join(suc, f'{value.get("name")}.{value.get("suffix")}'))
                # 合规但是重复
                elif value.get('legal') is True and value.get('dup') is True:
                    index = self.__dup_name_dict[value.get("name")].index(key)
                    copyfile(key,
                             os.path.join(dup, f'{value.get("name")}.{index}.{value.get("suffix")}'))
                else:
                    copyfile(key,
                             os.path.join(fail, f'{value.get("name")}.{value.get("suffix")}' or os.path.split(key)[1]))
        else:
            print(f'“{path}” 并非一个合法的路径！')

        return self


def main():
    """请自行寻找测试数据"""
    # PickStuNumber("./pics", show_img=False).print_info().write_out()
    # PickStuNumber("./pics/test.jpeg", show_img=True).print_info()
    # PickStuNumber("./pics/IMG.jpg", show_img=True).print_info()
    # PickStuNumber("./pics/IMG_023.jpg", show_img=True).print_info()
    # PickStuNumber("./pics/F6D35171-ECCF-4D28-BFF5-69B31453A2FB_big.jpg", show_img=True).write_out()
    pass


if __name__ == '__main__':
    main()
