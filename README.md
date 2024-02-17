### 阿狸工具
后端贴图Python服务实现 ，阿狸工具-专注提高工作效率

### 运行环境
- Python3.10.10+

### 安装

使用以下命令安装：
```bash
git clone git@github.com:cmxStarCoding/tools-python-pic-paste-server.git

pip install -r requirements.txt
```
项目配置：
```bash
#配置redis、mysql(在项目目录下新建config.ini文件)
[redis]
host = localhost
port = 6379
db = 0
password = None

[uvicorn]
host = 127.0.0.1
port = 8003

[app]
domain = http://127.0.0.1:8003

[notify]
batch_notify = http://127.0.0.1:8083/api/v1/pic_paste_notify

[oss]
access_key_id =
access_key_secret =
endpoint =
bucket_name =
domain =
endpoint_bucket =

```

运行：
```bash
cd tools-python-pic-paste-server
python3 main.py
```
### 作者
- 作者名字：崔明星
- 电子邮件：15638276200@163.com

### 贡献
如果你想为项目做出贡献，请通过邮箱15638276200@163.com联系。

