# -*- coding: utf-8 -*-

# Copyright 2013 CNA_Bld @ SSHZ.ORG
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import unicodedata
import sys
import codecs

if sys.platform == 'win32':
    win = True
else:
    win = False

VERSION = "V0.1"
RESX = 512
RESY = 384
LINE_SPACE = 2
CHAR_SPACE = 2

OUTPUT_HEAD = '''
[Script Info]
Title: BiliStarLocalDanmakuHandler
Original Script: 嗶哩嗶哩 - ( ゜- ゜)つロ 乾杯~
Script Updated By: BiliStar_BiliDanmakuModule ''' + VERSION + '''
ScriptType: v4.00+
Collisions: Normal
PlayResX: ''' + str(RESX) + '''
PlayResY: ''' + str(RESY) + '''
PlayDepth: 32
Timer: 100.0000
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, TertiaryColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Medium, 黑体,25,11861244,11861244,0,-2147483640,-1,0,0,0,100,100,1,0.00,1,1,0,2,30,30,30,1
Style: Big, 黑体,36,11861244,11861244,0,-2147483640,-1,0,0,0,100,100,2,0.00,1,1,0,2,30,30,30,1
Style: Small, 黑体,18,11861244,11861244,0,-2147483640,-1,0,0,0,100,100,1,0.00,1,1,0,2,30,30,30,1
Style: Compact, 黑体,18,11861244,11861244,0,-2147483640,-1,0,0,0,100,100,1,0.00,1,1,0,2,30,30,30,1
Style: BackG,  黑体,18,11861244,11861244,0,-2147483640,-1,0,0,0,100,100,1,0.00,1,1,0,2,30,30,30,1
Style: Default, 黑体,18,11861244,11861244,0,-2147483640,-1,0,0,0,100,100,1,0.00,1,1,0,10,30,30,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''

# ========================================


def chr_width(c):
    """
    返回字符显示宽度
    """
    if unicodedata.east_asian_width(c) in ('F', 'W', 'A'):
        return 2
    else:
        return 1


def win_encode(ori_str):
    """
    Windows 平台强制转换为 Unicode
    """
    if win:
        try:
            ori_str = unicode(ori_str, 'utf-8')
        except:
            pass  # 万一它本来就是 Unicode 字符串直接返回
    return ori_str


def win_repair():
    """
    Windows 平台统一修复函数
    """
    global OUTPUT_HEAD  # 下面那句调用它本体了不得不设成 Global
    OUTPUT_HEAD = win_encode(OUTPUT_HEAD)


# ========================================


def compare_danmaku(danmaku_a, danmaku_b):
    """
    比较弹幕时间，danmaku_a 较小或相等返回-1，否则1
    """
    if danmaku_a['oritime'] <= danmaku_b['oritime']:
        return -1
    else:
        return 1


def get_danmaku_size(orisize):
    """
    弹幕字体大小转换函数
    输入: 字符串型字体大小
    返回: 字符串型SSA用字体大小参数
    """
    if orisize == '18':
        return 'Small'
    elif orisize == '25':
        return 'Medium'
    elif orisize == '36':
        return 'Big'
    else:
        return 'Medium'  # 其它字号全部按 Medium 处理


def get_danmaku_time(oritime):
    """
    弹幕时间参数转换函数
    输入: 字符串型弹幕时间
    返回: 字符串型SSA用时间参数，格式『开始,结束』
    """
    if float(oritime) >= 0:
        fractional_part = oritime[oritime.find('.') + 1:oritime.find('.') + 3]
        start_time = time.strftime('%H:%M:%S', time.gmtime(float(oritime)))
        end_time = time.strftime('%H:%M:%S', time.gmtime(float(oritime) + 4))
        return start_time + '.' + fractional_part + ',' + end_time + '.' + fractional_part
    else:
        return '0:00:00.-20,0:00:03.79' # 在开始播放前发送弹幕则记录弹幕时间为0.-20


def str_length(string, size):
    """
    字符串宽度计算函数
    输入: 字符串, 字号
    返回: 整型
    """
    length = 0
    for char in string:
        length += chr_width(char)
    length = length * size / 2
    length += CHAR_SPACE * (len(string) - 1)
    return length


# ========================================


def xml_to_danmaku_dict(original_xml):
    """
    单行弹幕转换字典函数
    输入: 原始XML格式单行弹幕
    返回: 字典类型单行弹幕
    字典定义: {'time':SSA格式时间参数, 'oritime':浮点型原始时间, 'mode':弹幕模式, 'size':SSA风格弹幕尺寸, 'orisize':字符串类型原始尺寸, 'color':SSA标准型颜色参数, 'content': 弹幕内容}
    """
    result = {}
    result['oritime'] = float(original_xml[original_xml.find('"') + 1:original_xml.find(',')])
    result['time'] = get_danmaku_time(original_xml[original_xml.find('"') + 1:original_xml.find(',')])
    original_xml = original_xml[original_xml.find(',') + 1:]
    result['mode'] = original_xml[0]
    original_xml = original_xml[2:]
    result['orisize'] = original_xml[0:original_xml.find(',')]
    result['size'] = get_danmaku_size(original_xml[0:original_xml.find(',')])
    original_xml = original_xml[original_xml.find(',') + 1:]
    result['color'] = hex(int(original_xml[0:original_xml.find(',')]))[2:].upper()
    result['content'] = original_xml[original_xml.find('>') + 1:original_xml.find('<')]
    return result


def parse_xml(xml_data):
    """
    主XML解析函数
    输入: 原始XML格式字符串型完整弹幕
    返回: 列表式字典类型弹幕
    """
    xml_data = win_encode(xml_data)
    danmaku_list = []
    while xml_data.find('<d p=') != -1:
        danmaku_list.append(xml_to_danmaku_dict(xml_data[xml_data.find('<d p='):xml_data.find('</d>') + 4]))
        xml_data = xml_data[xml_data.find('</d>') + 5:]
    danmaku_list.sort(compare_danmaku)
    return danmaku_list


# ========================================


class ScreenController():
    """
    大工程 将ScreenControl事务打包成为一个类
    type属性控制类型。False为上到下，True下到上【内部存储倒过来存，返回定位参数时再倒过来输出就好= =】
    """

    def init_screen(self):
        """
        初始化自身
        """
        self.status = [0.] * (RESY + 1)
        self.status[0] = -1.
        return

    def remove_left_danmaku(self, current_time):
        """
        清除已离开控制区的弹幕
        输入: 当前时间
        """
        for point in range(1, RESY + 1):
            if self.status[point] < current_time:
                self.status[point] = 0.
        return

    def check_for_space(self, position, size):
        """
        检测该空间能否放下目标弹幕
        输入: 弹幕起始坐标, 弹幕大小
        返回: T/F
        """
        if position + size - 1 > RESY:  # 超出屏幕高度
            return False
        else:
            for point in range(position, position + size):
                if self.status[point] != 0.:
                    return False
            return True

    def add_danmaku(self, size, current_time, life_period=4):
        """
        增添作用中弹幕。
        输入: 整型弹幕高度, 当前时间, 占用时间秒
        返回: SSA用定位参数
        """
        self.remove_left_danmaku(current_time)
        flag = False
        for start_position in range(LINE_SPACE + 1, RESY):
            if (self.status[start_position] == 0.) and (self.check_for_space(start_position, size)):
                flag = True
                break
        if not flag:  # 无有效空间
            self.init_screen()
            start_position = 1
        for point in range(start_position, start_position + size + LINE_SPACE):
            self.status[point] = current_time + life_period
        if not self.type:
            return start_position + size - 1
        else:
            return RESY - start_position + 1

    def __init__(self, screen_type=False):
        self.init_screen()
        self.type = screen_type
        return


def parse_top_danmaku(danmaku_list):
    """
    顶部弹幕解析函数
    输入: 列表式字典类型顶部弹幕
    返回: 顶部弹幕SSA列表
    """
    screen = ScreenController(False)
    ssa_list = []
    for danmaku in danmaku_list:
        position = screen.add_danmaku(int(danmaku['orisize']), danmaku['oritime'], 4)
        ssa = {'ssa': u'Dialogue: 5,' + danmaku['time'] + u',' + danmaku['size'] + u',AcFun,0000,0000,0000,,{\\pos(' + str(RESX / 2) + u', ' + str(position) + u')\\c&H' + danmaku['color'] + u'\\fs' + danmaku['orisize'] + u'}' + danmaku['content'], 'time': danmaku['oritime']}
        ssa_list.append(ssa)
    return ssa_list


def parse_bottom_danmaku(danmaku_list):
    """
    底部弹幕解析函数
    输入: 列表式字典类型底部弹幕
    返回: 底部弹幕SSA列表
    """
    screen = ScreenController(True)
    ssa_list = []
    for danmaku in danmaku_list:
        position = screen.add_danmaku(int(danmaku['orisize']), danmaku['oritime'], 4)
        ssa = {'ssa': u'Dialogue: 5,' + danmaku['time'] + u',' + danmaku['size'] + u',AcFun,0000,0000,0000,,{\\pos(' + str(RESX / 2) + u', ' + str(position) + u')\\c&H' + danmaku['color'] + u'\\fs' + danmaku['orisize'] + u'}' +danmaku['content'], 'time': danmaku['oritime']}
        ssa_list.append(ssa)
    return ssa_list


def parse_rolling_danmaku(danmaku_list):
    """
    滚动弹幕解析函数
    输入: 列表式字典类型滚动弹幕
    返回: 滚动弹幕SSA列表
    """
    screen = ScreenController(False)
    ssa_list = []
    for danmaku in danmaku_list:
        length = str_length(danmaku['content'], int(danmaku['orisize']))
        life_time = 4. * (0.5 * length / (0.5 * length + RESX))
        position = screen.add_danmaku(int(danmaku['orisize']), danmaku['oritime'], life_time)
        ssa = {'ssa': u'Dialogue: 3,' + danmaku['time'] + u',' + danmaku['size'] + u',AcFun,0000,0000,0000,,{\\move(' + str(RESX + length / 2) + u', ' + str(position) + u', ' + str(-length / 2) + u', ' + str(position) + u')\\c&H' +danmaku['color'] + u'\\fs' + danmaku['orisize'] + u'}' + danmaku['content'], 'time': danmaku['oritime']}
        ssa_list.append(ssa)
    return ssa_list


# ========================================


def distribute_danmaku(danmaku_list):
    """
    弹幕主解析分发函数
    输入: 列表式字典类型弹幕
    返回: 弹幕SSA列表
    SSA字典定义: {'ssa':SSA内容, 'time':浮点原始时间戳}
    """
    top_danmaku = []
    bottom_danmaku = []
    rolling_danmaku = []
    ssa_list = []
    for danmaku in danmaku_list:
        if danmaku['mode'] in ('1', '2', '3', '7'):  # 高级弹幕强制认定为滚动弹幕
            rolling_danmaku.append(danmaku)
        elif danmaku['mode'] == '4':
            bottom_danmaku.append(danmaku)
        elif danmaku['mode'] == '5':
            top_danmaku.append(danmaku)
        elif danmaku['mode'] == '6':
            rolling_danmaku.append(danmaku)  # 这是逆向。。当滚动处理吧。。
        else:
            print(u'老婆快出来看啊有神弹幕！轨道：' + danmaku['mode'])
            #print(danmaku['content'])
            #rolling_danmaku.append(danmaku)  # 特效轨，脚本可能卡程序，暂时无视
    ssa_list.extend(parse_top_danmaku(top_danmaku))
    ssa_list.extend(parse_bottom_danmaku(bottom_danmaku))
    ssa_list.extend(parse_rolling_danmaku(rolling_danmaku))
    return ssa_list


def xml_to_ssa(xml_data):
    """
    主函数。
    输入: 原始XML
    返回: Unicode 编码 SSA文件
    """
    print('Parsing XML File...')
    try:
        danmaku_list = parse_xml(xml_data)
    except:
        print('FAILED.')
        return ''
    print('Converting to SSA...')
    try:
        ssa_list = distribute_danmaku(danmaku_list)
    except:
        print('FAILED.')
        return ''
    output_ssa = OUTPUT_HEAD
    for ssa_line in ssa_list:
        output_ssa += ssa_line['ssa'] + '\n'
    print('Converting Successfully Finished - Returning Result.')
    return output_ssa


def BiliStarHandler(xml_data, filename):
    """
    BiliStar 接口
    """
    print('BiliStar - BiliDanmaku Module Version: ' + VERSION)
    outfile = codecs.open(filename, 'w', 'utf-8')
    outfile.write(xml_to_ssa(xml_data))
    outfile.close()


# ========================================


win_repair()


def main():
    print('BiliStar - BiliDanmaku Module.\nVersion: ' + VERSION + '\n')
    filename = win_encode(input('Filename Please [For Windows: Use \'/\' instead of \'\\\']:'))
    if not filename.endswith('.xml'):
        print('Not a XML Danmaku File!')
        exit()
    print('\nOutput File: ' + filename[:-4] + '.ssa\n')
    xml_data = win_encode(open(filename).read())
    print('Converting...')
    output = codecs.open(filename[:-4] + '.ssa', 'w', 'utf-8')
    output.write(xml_to_ssa(xml_data))
    output.close()
    print('Finished.')


if __name__ == '__main__':
    main()
