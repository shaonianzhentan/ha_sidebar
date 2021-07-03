import json, os, shutil, hashlib, base64, yaml

class ApiConfig():

    def __init__(self, _dir):        
        if os.path.exists(_dir) == False:           
            self.mkdir(_dir)
        self.dir = _dir

    # 创建文件夹
    def mkdir(self, path):
        folders = []
        while not os.path.isdir(path):
            path, suffix = os.path.split(path)
            folders.append(suffix)
        for folder in folders[::-1]:
            path = os.path.join(path, folder)
            os.mkdir(path)

    # 获取路径
    def get_path(self, name):
        return self.dir + '/' + name

    # 读取文件内容
    def read(self, name):
        fn = self.get_path(name)
        if os.path.isfile(fn):
            with open(fn,'r', encoding='utf-8') as f:
                content = yaml.load(f, Loader=yaml.FullLoader)
                return content
        return None

    # 写入文件内容
    def write(self, name, obj):
        with open(self.get_path(name), 'w', encoding='utf-8') as f:
            yaml.dump(obj, f)