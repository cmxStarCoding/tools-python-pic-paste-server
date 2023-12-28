import configparser
import os
import oss2
# -*- coding: utf-8 -*-
import os
from oss2 import SizedFileAdapter, determine_part_size
from oss2.models import PartInfo
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider


# 创建一个ConfigParser对象
config = configparser.ConfigParser()
# 读取配置文件
config.read('config.ini')


def upload_to_oss(local_file_path, oss_file_path):
    # 阿里云 OSS 访问信息
    print("开始上传文件到OSS")
    access_key_id = config['oss']['access_key_id']
    access_key_secret = config['oss']['access_key_secret']
    endpoint = config['oss']['endpoint']
    bucket_name = config['oss']['bucket_name']
    domain = config['oss']['domain']
    endpoint_bucket = config['oss']['endpoint_bucket']

    # 创建 OSS 客户端
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    # 上传文件的本地路径
    # local_file_path = '../static/result_images_zyzccx_1700226471.zip'
    # object_key = 'img'  # 存储在 OSS 上的对象名称

    # 填写不能包含Bucket名称在内的Object完整路径，例如exampledir/exampleobject.txt。
    key = oss_file_path
    # key = 'exampledir/exampleobject.zip'
    # 填写本地文件的完整路径，例如D:\\localpath\\examplefile.txt。
    filename = local_file_path

    total_size = os.path.getsize(filename)
    # determine_part_size方法用于确定分片大小。
    part_size = determine_part_size(total_size, preferred_size=100 * 1024)

    upload_id = bucket.init_multipart_upload(key).upload_id

    parts = []

    # 逐个上传分片。
    with open(filename, 'rb') as file_obj:
        part_number = 1
        offset = 0
        while offset < total_size:
            num_to_upload = min(part_size, total_size - offset)
            # 调用SizedFileAdapter(file_obj, size)方法会生成一个新的文件对象，重新计算起始追加位置。
            result = bucket.upload_part(key, upload_id, part_number,
                                        SizedFileAdapter(file_obj, num_to_upload))
            parts.append(PartInfo(part_number, result.etag))

            offset += num_to_upload
            part_number += 1

    # 完成分片上传。
    # 如需在完成分片上传时设置相关Headers，请参考如下示例代码。
    headers = dict()
    res_url = bucket.complete_multipart_upload(key, upload_id, parts, headers=headers).resp.response.url
    res_url = res_url.replace('%2F', '/').split('?')[0]
    res_url = res_url.replace(endpoint_bucket, domain)
    return res_url

