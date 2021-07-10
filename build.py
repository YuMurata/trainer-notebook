'''
`python main.py`を実行したときにエラーが出る場合、
`python build.py`で生成したexeファイルを実行すると
`failed to execute script main`と表示される（多分）
'''
import subprocess

if __name__ == '__main__':
    command = 'pyinstaller'
    file_path = 'main.py'

    noconfirm = ['--noconfirm']
    add_data = ['--add-data', 'resource;resource']
    app_name = ['--name', 'umaumadrive']
    windowed = ['--windowed']
    option_list = noconfirm+add_data+app_name+windowed
    subprocess.run([command, file_path]+option_list)
