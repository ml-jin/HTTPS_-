# coding=utf-8
# Python 2
"""
除了安装Flask，还需要安装 Python 的 openssl 的类库：
pip install pyOpenSSL
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World"

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
