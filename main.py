import os
import time
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from common.utils import download_file, unzip_file, download_image, draw_circle, draw_square, paste_circle, parse_filename, zip_folder, delete_folder, generate_random_string
from common.file_cache import FileCache
from common.up_to_oss import upload_to_oss
import asyncio
import configparser
import requests
import json

# 创建一个ConfigParser对象
config = configparser.ConfigParser()

# 读取配置文件
config.read('config.ini')

app = FastAPI()
# 允许所有来源的跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/image-plus/static", StaticFiles(directory="./static"), name="static")
host = config['uvicorn']['host']
port = int(config['uvicorn']['port'])
domain = config['app']['domain']
file_cache = FileCache()


async def long_running_task(original_image_url, compress_file_url, batch_no, x, y, r, type, multiple, is_square, side_length):
    os.makedirs('./save/' + batch_no, exist_ok=True)
    # 下载并保存文件
    save_path = './save/' + batch_no + '/' + batch_no + '.zip'
    download_file(compress_file_url, save_path)
    # 下载底图
    original_save_path = "./save/" + batch_no + '/'
    original_image_info = download_image(original_image_url, original_save_path, 'original_image')
    # 解压文件
    extract_path = './save/' + batch_no
    unzip_file(save_path, extract_path)

    folder_path = './save/' + batch_no + '/' + parse_filename(compress_file_url) + '/'
    original_image_path = './save/' + batch_no + '/' + original_image_info['full_file_name']
    draw_save_path = './save/' + batch_no + '/' + 'background_' + original_image_info['full_file_name']

    if is_square == 0:
        background_img_info = draw_circle(original_image_path, draw_save_path, x, y, r)
    else:
        background_img_info = draw_square(original_image_path, draw_save_path, x, y, side_length)

    for root, dirs, files in os.walk(folder_path, topdown=False):
        total_num = len(files)
        zero = 0
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, folder_path)
            if relative_path == '.DS_Store':
                continue
            zero = zero + 1
            paste_circle(background_img_info, folder_path + relative_path, folder_path, relative_path, x, y, type, multiple)
            file_cache.set(batch_no, round(zero/total_num, 2))

    # 压缩文件 压缩包上传到oss 通知php
    folder_path = './save/' + batch_no + '/' + parse_filename(compress_file_url)
    output_path = './save/' + batch_no + '/' + parse_filename(compress_file_url) + '.zip'
    zip_folder(folder_path, output_path)

    if os.path.exists(output_path):
        # oss_url = upload_to_oss(output_path, 'zip/' + parse_filename(compress_file_url) + '.zip')
        # 删除文件 上传到oss时可以删除文件
        # delete_folder('./save/' + batch_no)
        # print(oss_url, '异步任务完成oss_url')
        url = config['notify']['batch_notify']
        headers = {'Content-Type': 'application/json'}
        data = {'batch_no': batch_no, 'status': 1}

        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            response_data = response.json()

            print("回调返回数据", response_data)
        else:
            print(batch_no + '回调请求失败，状态码：', response.status_code)
    else:
        print(batch_no + '文件压缩失败：')


def run_in_thread(fn):
    def run(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(fn(*args, **kwargs))

    return run


@app.post("/qrcode-replace/debug")
async def forward(request: Request):
    data = await request.json()
    original_image_url = data.get('original_image_url', '')
    stick_img_url = data.get('stick_img_url', '')
    x = data.get('x', 0)
    y = data.get('y', 0)
    r = data.get('r', 0)
    type = data.get('type', 0)
    multiple = data.get('multiple', 0)
    is_square = data.get('is_square', 0)
    side_length = data.get('side_length', 100)
    save_path = './save/debug/' + generate_random_string(4) + '/'

    os.makedirs(save_path + 'draw_circle', exist_ok=True)
    os.makedirs(save_path + 'result', exist_ok=True)

    # 底图
    original_image_filename = parse_filename(original_image_url) + generate_random_string(4)
    original_image_full_name = download_image(original_image_url, save_path, original_image_filename)
    original_image_full_path = save_path + original_image_full_name['full_file_name']

    # 贴图
    stick_image_filename = parse_filename(stick_img_url) + generate_random_string(4)
    stick_image_full_name = download_image(stick_img_url, save_path, stick_image_filename)
    stick_image_full_path = save_path + stick_image_full_name['full_file_name']

    # 画圆
    draw_save_path = save_path + 'draw_circle/' + original_image_full_name['full_file_name']

    if is_square == 0:
        draw_circle(original_image_full_path, draw_save_path, int(x), int(y), int(r))
    else:
        draw_square(original_image_full_path, draw_save_path, int(x), int(y), int(side_length))

    # 合成
    result_draw_save_path = save_path + 'result/'
    paste_circle(draw_save_path, stick_image_full_path, result_draw_save_path, original_image_full_name['full_file_name'], int(x), int(y), int(type), float(multiple))

    upload_oss_file_path = result_draw_save_path + original_image_full_name['full_file_name']
    oss_url = upload_to_oss(upload_oss_file_path, 'static/' + original_image_full_name['full_file_name'])
    # 删除文件
    delete_folder(save_path)
    print(oss_url)
    return {"image_url": oss_url}


@app.post("/qrcode-replace/replace")
async def forward(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    original_image_url = data.get('original_image_url', '')
    compress_file_url = data.get('compress_file_url', '')
    x = data.get('x', 0)
    y = data.get('y', 0)
    r = data.get('r', 0)
    type = data.get('type', 0)
    multiple = data.get('multiple', 0)
    batch_no = data.get('batch_no', '')
    is_square = data.get('is_square', 0)
    side_length = data.get('side_length', 100)
    do_replace = run_in_thread(long_running_task)

    background_tasks.add_task(do_replace, original_image_url, compress_file_url, batch_no, int(x), int(y), int(r), int(type), float(multiple), int(is_square), int(side_length))
    return {"message": 'ok'}


@app.get("/qrcode-replace/schedule/info")
async def plus_info(request: Request):
    batch_no = request.query_params.get('batch_no')
    schedule = file_cache.get(batch_no)
    return {'schedule': schedule}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app='main:app', host=host, port=port, use_colors=True, workers=4)
