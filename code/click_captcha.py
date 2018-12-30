#!/usr/bin/python
# -*- coding: UTF-8 -*-
from PIL import Image, ImageDraw, ImageFont
import random
import json
import os
import time


class ClickCaptcha(object):
    def __init__(self):
        # 图片设置
        self.width = 320  # 宽度
        self.height = 160  # 高度
        self.mode = "RGB"  # 图片生成模式
        self.no_steps = self.height  # 渐变迭代次数

        # 文字设置
        self.add_text = True
        self.word_count_min = 3
        self.word_count_max = 5
        self.word_size = 32  # 字体大小
        self.word_offset = 5  # 字符之间的最小距离
        self.width_left_offset = 10  # 字符距离边界的距离
        self.width_right_offset = 40
        self.height_top_offset = 10
        self.height_bottom_offset = 40
        # 字体和字符集
        self.font_path = "C:/windows/fonts/simkai.ttf"  # 字体路径
        self.set_font = ImageFont.truetype(self.font_path, self.word_size)  # 设置字体
        self.word_list = list()  # 字符集：字符集从文件中读取的时候必须是数组形式
        with open("../data/chinese_word.json", "r", encoding="utf-8") as f:
            self.word_list = json.load(f)

        # 干扰线
        self.interference_line = False
        self.inter_line_min = 10
        self.inter_line_max = 16
        self.interference_line_width = 3
        self.interference_line_radius = (-40, 40)

        # 虚构文字
        self.dummy_word = True
        self.dummy_word_width = 2  # 虚构文字的线宽度
        self.dummy_word_count_min = 3
        self.dummy_word_count_max = 5
        self.dummy_word_strokes_min = 6
        self.dummy_word_strokes_max = 15
        self.dummy_word_color = (0, 0, 0)

        # 图片保存路径
        self.save_status = True
        self.image_postfix = "jpg"
        self.label_postfix = "txt"
        self.save_img_dir = "../image245/img"
        self.save_label_dir = "../image245/label"
        # 判断文件夹是否存在
        if not os.path.exists(self.save_img_dir):
            os.mkdir(self.save_img_dir)
        if not os.path.exists(self.save_label_dir):
            os.mkdir(self.save_label_dir)

        # 内部参数
        self.word_point_list = None
        self.img = None
        self.draw = None
        self.word_count = None
        self.gradient = None
        self.label_string = None

    @staticmethod
    def gen_random_color():
        """
        获取随机的一种背景色（去掉了偏黑系颜色）
        :return:
        """
        a = random.randint(0, 255)
        b = random.randint(50, 255)
        c = random.randint(50, 255)
        return a, b, c

    @staticmethod
    def gen_random_line_color():
        """
        获取随机的线条颜色
        :return:
        """
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        c = random.randint(0, 255)
        return a, b, c

    @staticmethod
    def lerp_colour(c1, c2, t):
        """
        计算每层的渐变色数值
        :param c1:
        :param c2:
        :param t:
        :return:
        """
        return int(c1[0] + (c2[0] - c1[0]) * t), int(c1[1] + (c2[1] - c1[1]) * t), int(c1[2] + (c2[2] - c1[2]) * t)

    def init_gradient(self):
        """
        生成渐变色列表
        :return:
        """
        list_of_colors = [self.gen_random_color(), self.gen_random_color(),
                          self.gen_random_color(), self.gen_random_color()]

        for i in range(len(list_of_colors) - 2):
            for j in range(self.no_steps):
                self.gradient.append(self.lerp_colour(list_of_colors[i], list_of_colors[i + 1], j / self.no_steps))

    def init_gradient_image_draw(self):
        """
        生成一张渐变色背景的图片
        :param gradient:
        :return:
        """
        self.img = Image.new(self.mode, (self.width, self.height), (0, 0, 0))

        for i in range(self.height):
            for j in range(self.width):
                self.img.putpixel((j, i), self.gradient[j])
        self.draw = ImageDraw.Draw(self.img)

    def generate_random_location(self, i_num):
        """
        生成一个随机的位置，且判断不与之前的位置重合
        :param i_num:
        :return:
        """
        print("=== <word index: {}> start generate random location (x, y)".format(i_num))
        while True:
            print(">>> start judge <<<")
            judge = [False] * i_num
            normal = [True] * i_num
            location_x = random.randint(self.width_left_offset, self.width - self.width_right_offset)
            location_y = random.randint(self.height_top_offset, self.height - self.height_bottom_offset)
            print("word_point_list: {}".format(self.word_point_list))
            print("right now (x, y) -> ({}, {})".format(location_x, location_y))
            for index, wp in enumerate(self.word_point_list):
                x1, y1 = wp
                if location_x > x1 + self.word_size + self.word_offset:
                    judge[index] = True
                elif location_x + self.word_size + self.word_offset < x1:
                    judge[index] = True
                elif location_y > y1 + self.word_size + self.word_offset:
                    judge[index] = True
                elif location_y + self.word_size + self.word_offset < y1:
                    judge[index] = True
                else:
                    print("(x, y)->({}, {}) interference to word_point_list!".format(location_x, location_y))
                    continue

            if judge == normal:
                print("(x, y) -> ({}, {}) -> pass".format(location_x, location_y))
                return location_x, location_y

    def add_text_to_images(self):
        """
        添加文字到图片
        :return:
        """
        captcha_info = dict()
        captcha_info["word"] = list()
        for i in range(0, self.word_count):
            # 生成随机位置 + 避免互相干扰
            location_x, location_y = self.generate_random_location(i)

            # 对象位置加入到列表
            self.word_point_list.append([location_x, location_y])

            # 随机选择文字并绘制
            word = random.choice(self.word_list)
            print("Put word {} success!".format(word))
            self.draw.text((location_x, location_y), word, font=self.set_font, fill=(0, 0, 0))
            info = {"x": location_x,
                    "y": location_y,
                    "word": word}
            captcha_info["word"].append(info)
        captcha_info["word_width"] = self.word_size
        return captcha_info

    def add_interference_line(self):
        """
        添加干扰线
        :return:
        """
        num = random.randint(self.inter_line_min, self.inter_line_max)
        for i in range(num):
            line_x = random.randint(self.width_left_offset, self.width - self.width_right_offset)
            line_y = random.randint(self.height_top_offset, self.height - self.height_bottom_offset)
            line_x_offset = random.randint(*self.interference_line_radius)
            line_y_offset = random.randint(*self.interference_line_radius)
            start_point = (line_x, line_y)
            end_point = (line_x + line_x_offset, line_y + line_y_offset)
            self.draw.line([start_point, end_point], self.gen_random_line_color(), width=self.interference_line_width)
        return self.draw

    def add_dummy_word(self):
        """
        添加虚拟文字
        :return:
        """
        # 虚构文字数量
        num_a = random.randint(self.dummy_word_count_min, self.dummy_word_count_max)
        for i in range(num_a):
            # 虚构文字笔画数
            num_b = random.randint(self.dummy_word_strokes_min, self.dummy_word_strokes_max)

            # 生成随机位置+避免互相干扰
            location_x, location_y = self.generate_random_location(i + self.word_count)

            self.word_point_list.append([location_x, location_y])
            # 确定位置后开始生成坐标
            bx = random.randint(location_x, location_x + self.word_size)  # x'
            by = random.randint(location_y, location_y + self.word_size)  # y'
            line_x_end = location_x + self.word_size  # x + 20
            line_y_end = location_y + self.word_size  # y + 20
            a = (bx, location_y)
            b = (line_x_end, by)
            c = (bx, line_y_end)
            d = (location_x, by)
            for j in range(num_b):
                draw_type = random.randint(1, 6)
                if draw_type == 1:
                    self.draw.line([a, b], self.dummy_word_color, width=self.dummy_word_width)
                elif draw_type == 2:
                    self.draw.line([a, c], self.dummy_word_color, width=self.dummy_word_width)
                elif draw_type == 3:
                    self.draw.line([a, d], self.dummy_word_color, width=self.dummy_word_width)
                elif draw_type == 4:
                    self.draw.line([b, c], self.dummy_word_color, width=self.dummy_word_width)
                elif draw_type == 5:
                    self.draw.line([b, d], self.dummy_word_color, width=self.dummy_word_width)
                else:  # this is 6 type
                    self.draw.line([c, d], self.dummy_word_color, width=self.dummy_word_width)

    def save_images(self, order_num):
        """
        保存图片和标签
        :param order_num:
        :return:
        """
        tc = str(time.time()).replace(".", "")
        # 图片
        img_file = "{}_{}.{}".format(order_num, tc, self.image_postfix)
        img_path = os.path.join(self.save_img_dir, img_file)
        self.img.save(img_path)

        # 标签
        label_file = "{}_{}.{}".format(order_num, tc, self.label_postfix)
        label_path = os.path.join(self.save_label_dir, label_file)
        with open(label_path, "w") as f:
            content = json.dumps(self.label_string, ensure_ascii=False)
            f.write(content)

    def create_image_with_config(self, order_num):
        """
        根据配置生成一张图片
        :param order_num:序号
        :return:
        """
        print("\n--------------------- Generate picture <{}>  -----------------------: ".format(order_num))
        # 初始化绘画对象和所有对象的位置
        self.gradient = list()
        self.init_gradient()
        self.init_gradient_image_draw()
        self.word_point_list = []
        self.word_count = random.randint(self.word_count_min, self.word_count_max)

        # 添加文字
        if self.add_text:
            captcha_info = self.add_text_to_images()
            self.label_string = captcha_info

        # 创建干扰线
        if self.interference_line:
            self.add_interference_line()

        # 创建干扰虚构文字
        if self.dummy_word:
            self.add_dummy_word()

        # 保存图片
        if self.save_status:
            self.save_images(order_num)

    def generate_click_captcha(self, count=5):
        """
        生成指定数量的图片
        :param count:
        :return:
        """
        self.save_status = True
        for i in range(count):
            self.create_image_with_config(i)

    def show_exp(self):
        pass


def main():
    c = ClickCaptcha()
    c.generate_click_captcha()


if __name__ == '__main__':
    main()


