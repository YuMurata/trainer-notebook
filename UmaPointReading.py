import pyocr
import pyocr.builders
import difflib


class UmaPointReader:
    def __init__(self, tool, all_uma_name_list: list):
        self.tool = tool
        self.all_uma_name_list = all_uma_name_list

    def _ExtractUmaPt(self, line: str):
        ret_pt = None
        ret_name = None
        tmp = line.replace(',', '').replace('.', '').replace('、', '')

        for word in tmp.split(' '):
            if 'pt' in word:
                if word.split('pt')[0].isdecimal():
                    ret_pt = int(word.split('pt')[0])
                else:
                    print(word)
                    return None, None
        if ret_pt is None:
            return None, None

        extract_name = tmp.replace(' ', '').split(str(ret_pt))[0]
        max_match = 0
        for uma_name in self.all_uma_name_list:
            r = difflib.SequenceMatcher(None, uma_name, extract_name).ratio()
            if r > max_match:
                ret_name = uma_name
                max_match = r

        if max_match < 0.6:
            return None, None

        return ret_name, ret_pt

    def UmaPtListfromImage(self, img):
        builder = pyocr.builders.LineBoxBuilder(tesseract_layout=6)
        res = self.tool.image_to_string(img, lang="jpn", builder=builder)
        uma_pt_dict = {}

        for d in res:
            uma, pt = self._ExtractUmaPt(d.content)
            if uma is not None:
                uma_pt_dict[uma] = pt

        return uma_pt_dict
