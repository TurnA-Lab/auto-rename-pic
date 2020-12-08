#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'iskye'

import ctypes
import platform
import subprocess

import PySimpleGUI as sg

from pick_stu_number import PickStuNumber


def exe_cmd_subprocess(command, *args):
    try:
        sp = subprocess.Popen([command, *args], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = sp.communicate()
        if out:
            print(out.decode("utf-8"))
        if err:
            print(err.decode("utf-8"))
    except Exception:
        pass


def make_dpi_aware():
    """
    高清分辨率
    来源：https://github.com/PySimpleGUI/PySimpleGUI/issues/1179#issuecomment-475899050
    """
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)


def main():
    make_dpi_aware()

    # 设置主题
    sg.theme('Material 1')

    # 图片文件夹路径
    img_folder = {
        'key': '-ImgFolder-',
        'default': '.'
    }
    # 是否显示图片
    show_img = {
        'key': '-ShowImg-',
        'keyT': '-ShowImgT-',
        'keyF': '-ShowImgF-',
        'default': False
    }
    # 输出路径
    output = {
        'key': '-Output-',
        'default': '.'
    }
    # 合规且不重复
    output_suc = {
        'key': '-OutputSuc-',
        'default': 'output_suc'
    }
    # 合规但是重复
    output_dup = {
        'key': '-OutputDup-',
        'default': 'output_dup'
    }
    # 不合规
    output_fail = {
        'key': '-OutputFail-',
        'default': 'output_fail'
    }

    # 开始执行
    basic = [[sg.Text('请选择图片所在文件夹路径')],
             [sg.Input(sg.user_settings_get_entry(img_folder.get('key'),
                                                  img_folder.get('default')),
                       key=img_folder.get('key'), size=(25, 1)),
              sg.FolderBrowse(button_text='浏览')],
             [sg.OK(button_text='立即开始')],
             [sg.Output(size=(40, 10))]]

    # 配置
    config = [[sg.Frame(title='处理配置',
                        layout=
                        [[sg.Column(
                            size=(320, 60),
                            layout=
                            [[sg.Text('显示处理图片过程', size=(18, 1)),
                              sg.Radio('是', 'show_img',
                                       default=sg.user_settings_get_entry(
                                           show_img.get('key'), show_img.get('default')) is True,
                                       key=show_img.get('key')),
                              sg.Radio('否', 'show_img',
                                       default=sg.user_settings_get_entry(
                                           show_img.get('key'), show_img.get('default')) is False)]]
                        )]])
               ],
              [sg.Frame(title='输出配置',
                        layout=
                        [[sg.Column(
                            size=(320, 160),
                            layout=
                            [[sg.Text('输出路径', size=(18, 1)),
                              sg.Input(sg.user_settings_get_entry(output.get('key'), output.get('default')),
                                       key=output.get('key'), size=(6, 1)),
                              sg.FolderBrowse(button_text='浏览')],
                             [sg.Text('合规图片文件夹名', size=(18, 1)),
                              sg.Input(sg.user_settings_get_entry(output_suc.get('key'), output_suc.get('default')),
                                       key=output_suc.get('key'), size=(15, 1))],
                             [sg.Text('重复图片文件夹名', size=(18, 1)),
                              sg.Input(sg.user_settings_get_entry(output_dup.get('key'), output_dup.get('default')),
                                       key=output_dup.get('key'), size=(15, 1))],
                             [sg.Text('其它图片文件夹名', size=(18, 1)),
                              sg.Input(sg.user_settings_get_entry(output_fail.get('key'), output_fail.get('default')),
                                       key=output_fail.get('key'), size=(15, 1))]]
                        )]])
               ],
              [sg.OK(button_text='保存')]]

    # 选项卡
    layout = [[sg.TabGroup(layout=[[sg.Tab('开始', basic), sg.Tab('配置', config)]])]]

    # 显示的窗口
    window = sg.Window(title='青年大学习截图重命名',
                       margins=(30, 30),
                       font=('Microsoft YaHei', 10),
                       finalize=True,
                       layout=layout).finalize()

    # 处理事件
    while True:
        event, values = window.read()

        # print(event, values)
        if event == sg.WIN_CLOSED:
            break
        elif event == '立即开始':
            print('即将开始处理图片')
            print('请在处理完毕后再关闭本窗口\n')
            print('-' * 30)

            PickStuNumber(values.get(img_folder.get('key')), values.get(show_img.get('key'))).write_out(
                values.get(output.get('key')), values.get(output_suc.get('key')),
                values.get(output_dup.get('key')),
                values.get(output_fail.get('key')))

            print()
            print('-' * 30)
            print('处理完毕')

        elif event == '保存':
            for key in {img_folder.get('key'), show_img.get('keyT'), output.get('key'),
                        output_suc.get('key'), output_dup.get('key'), output_fail.get('key')}:
                if key is show_img.get('keyT'):
                    sg.user_settings_set_entry(show_img.get('key'), values.get(show_img.get('key')))
                else:
                    sg.user_settings_set_entry(key, values.get(key))

    # 关闭窗口
    window.close()
    pass


if __name__ == '__main__':
    main()
