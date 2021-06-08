import pyocr
import pyocr.builders
import difflib

class UmaPointReading():

    tool = None

    def __init__(self, tool):

        self.tool = tool

    def setUmaList(self, uma_name_list:list):
        self.uma_name_list = uma_name_list


    def __isint(self, s):  # 整数値を表しているかどうかを判定
        try:
            int(s)  # 文字列を実際にint関数で変換してみる
        except ValueError:
            return False
        else:
            return True

    def __ExtractUmaPt(self, line:str):
        ret_pt = None
        ret_name = None
        tmp = line.replace(',', '').replace('.', '').replace('、', '')

        for word in tmp.split(' '):
            if 'pt' in word:
                if self.__isint(word.split('pt')[0]):
                    ret_pt = int(word.split('pt')[0])
                else:
                    print(word)
                    return None,None
        if ret_pt is None:
            return None, None

        extract_name = tmp.replace(' ', '').split(str(ret_pt))[0]
        max_match = 0
        for uma_name in self.uma_name_list:
            r = difflib.SequenceMatcher(None, uma_name, extract_name).ratio()
            if r > max_match:
                ret_name = uma_name
                max_match = r

        if max_match < 0.6:
            return None, None

        return ret_name, ret_pt

    def UmaPtListfromImage(self, img):
        res = self.tool.image_to_string(img,
                                    lang="jpn",
                                    builder=pyocr.builders.LineBoxBuilder(tesseract_layout=6))
        uma_pt_rank = {}
        for d in res:
            uma, pt = self.__ExtractUmaPt(d.content)
            if uma is not None:
                uma_pt_rank[uma] = pt

        return uma_pt_rank