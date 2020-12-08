#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'iskye'

import click

from pick_stu_number import PickStuNumber


@click.command()
@click.option('--path', default='.', help='图片或者图片所在文件夹的路径')
@click.option('--show-img', default=False, help='是否展示处理图片过程')
@click.option('--show-info', default=False, help='是否展示处理图片结果')
@click.option('--output', default='.', help='图片输出到的文件夹路径')
@click.option('--output-suc', default='output_suc', help='合规且不重复图片所在的文件夹名')
@click.option('--output-dup', default='output_dup', help='合规但是重复图片所在的文件夹名')
@click.option('--output-fail', default='output_fail', help='其它图片所在的文件夹名')
@click.help_option(help='显示帮助')
def main(path,
         show_img,
         show_info,
         output,
         output_suc,
         output_dup,
         output_fail):
    """自动重命名图片为学号"""
    psn = PickStuNumber(path, show_img).write_out(output, output_suc, output_dup, output_fail)
    if show_info:
        psn.print_info()
    pass


if __name__ == '__main__':
    main()
