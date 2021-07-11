'''
# exe作成方法
```
pip install -r requirements.txt
python build.py
```

# exe作成場所
```
dist/umaumadrive.exe
```

> **NOTE**
>
> `python main.py`を実行したときにエラーが出る場合、
> `python build.py`で生成したexeファイルを実行すると
> `failed to execute script main`と表示される（多分）

> **NOTE**
>
> microsoft storeからインストールしたpythonだと動かない可能性あり
> https://bitwalk.blogspot.com/2020/10/pyinstaller.html
>
> 普通？のpythonインストール方法
> https://www.python.jp/install/windows/install.html
'''
import subprocess

if __name__ == '__main__':
    command = 'pyinstaller'
    file_path = 'main.py'

    noconfirm = ['--noconfirm']
    add_data = ['--add-data', 'resource;resource']
    app_name = ['--name', 'trainer_notebook']
    windowed = ['--windowed']
    option_list = noconfirm+add_data+app_name+windowed
    subprocess.run([command, file_path]+option_list)
