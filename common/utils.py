import os
import random
import string
from PIL import Image, ImageDraw, ImageColor
import urllib.request
import zipfile
import requests
import imghdr
import zipfile
import os
import shutil


def delete_folder(folder_path):
    # 删除文件夹及其内容
    shutil.rmtree(folder_path)


def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))


def download_image(img_url, save_path, filename):
    response = requests.get(img_url)
    os.makedirs(save_path, exist_ok=True)
    if response.status_code == 200:
        content_type = response.headers.get('content-type')
        ext = '.jpg'
        if 'image' in content_type:
            ext = '.' + imghdr.what(None, h=response.content)
        # 保存图片到infile目录
        with open(f"{save_path}{filename + ext}", "wb") as f:
            f.write(response.content)
            f.close()
        return {'full_file_name': filename + ext}


def get_file_extension(file_name):
    # 使用os.path.splitext来获取文件名和扩展名的元组
    _, extension = os.path.splitext(file_name)
    return extension


def parse_filename(url):
    filename_with_extension = os.path.basename(url)
    filename, _ = os.path.splitext(filename_with_extension)
    return filename


def download_file(url, save_path):
    urllib.request.urlretrieve(url, save_path)


def unzip_file(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)


def draw_square(image_path, save_path, x, y, side_length, bc_color):
    # 打开图片并转换为RGB模式
    img = Image.open(image_path).convert("RGB")
    # 创建一个可以在图片上绘图的对象
    draw = ImageDraw.Draw(img)
    # 设置正方形区域的坐标点
    left = x - side_length // 2
    top = y - side_length // 2
    right = x + side_length // 2
    bottom = y + side_length // 2
    square_coordinates = (left, top, right, bottom)
    # 绘制正方形区域
    draw.rectangle(square_coordinates, fill=bc_color)
    # 保存修改后的图片
    img.save(save_path)
    return save_path


# 指定坐标点画白色圆形区域，保存新图
def draw_circle(image_path, save_path, x, y, r, bc_color):
    # 打开图片并转换为RGB模式
    img = Image.open(image_path).convert("RGB")
    # 创建一个可以在图片上绘图的对象
    draw = ImageDraw.Draw(img)
    # 将十六进制颜色值转换为 RGB 格式
    bc_color_rgb = ImageColor.getrgb(bc_color)
    # 设置圆形区域的坐标点和半径
    circle_coordinates = (x - r, y - r, x + r, y + r)
    # 绘制圆形区域
    draw.ellipse(circle_coordinates, fill=bc_color_rgb)
    # 保存修改后的图片
    img.save(save_path)

    return save_path


# 调用函数来绘制圆形区域并保存
# draw_circle("./img/zhuotie.jpg", 380, 1100, 300)


# draw_circle("./img/zhuotie.jpg", 300, 500, 300)


# 合成新图并保存
def paste_circle(image_path, circle_image_path, folder_path, relative_path, x, y, type, multiple):
    # 打开背景图片
    background_img = Image.open(image_path).convert("RGBA")
    # 打开圆形图片
    circle_img = Image.open(circle_image_path)
    # 确保图像有透明度通道
    circle_img = circle_img.convert("RGBA")

    if type == 1:
        # 计算圆形图片的左上角坐标
        circle_x = x - int(circle_img.width * multiple) // 2
        circle_y = y - int(circle_img.height * multiple) // 2
        # 缩放圆形图片
        circle_img = circle_img.resize((int(circle_img.width * multiple), int(circle_img.height * multiple)))
    elif type == 2:
        # 计算圆形图片的左上角坐标
        circle_x = x - int(circle_img.width/multiple) // 2
        circle_y = y - int(circle_img.height/multiple) // 2
        # 缩放圆形图片
        circle_img = circle_img.resize((int(circle_img.width/multiple), int(circle_img.height/multiple)))
    else:
        circle_x = x - int(circle_img.width / 2)
        circle_y = y - int(circle_img.height / 2)
        circle_img = circle_img.resize((int(circle_img.width), int(circle_img.height)))
    # 在背景图片上粘贴圆形图片
    background_img.paste(circle_img, (circle_x, circle_y), mask=circle_img)

    # 保存生成的新图片
    background_img.convert("RGB").save(folder_path + relative_path)


# 调用函数来生成新图片
# paste_circle("./img/output.png", "./img/5266.png", 380, 1100)
# paste_circle("./img/output.png", "./img/5266.png", 300, 500)


def generate_random_string(length):
    # 所有的字符集
    chars = string.ascii_letters + string.digits
    # 使用random.choices随机选择4个字符
    random_string = ''.join(random.choices(chars, k=length))
    return random_string
