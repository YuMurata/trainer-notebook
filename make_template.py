from PIL import Image
from Uma import UmaNameFileReader
from snip import ImageSnipper


def create_template_img(img: Image.Image):
    template = img.crop((26, 70, 82, 129))
    aspect_ratio = template.width / template.height

    target_width = 69

    target_height = (int)(target_width / aspect_ratio)
    template = template.resize((target_width, target_height))

    template = template.crop(
        (15, 5, template.width - 15, template.height - 15))

    return template


if __name__ == '__main__':
    '''
    メニュー→ウマ娘名鑑→トレーナーノート→任意のうま娘→ボイス
    の画面で実行
    '''

    all_uma_name_list = UmaNameFileReader.Read()
    uma_name = None
    while uma_name not in all_uma_name_list:
        uma_name = input("作成するウマ娘の名前を入力してください\n->") + '\n'

    snip_img = ImageSnipper().Snip()
    template = create_template_img(snip_img)
    template.save(f"./resource/uma_template/{uma_name}.png")
