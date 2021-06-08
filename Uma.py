from collections import UserDict
import numpy as np
from pathlib import Path
        self.WriteUmaList()

    def readUmaList(self):
        self.uma_pt_dict = {}

        if not Path(self.resource_path).exists():
            raise FileNotFoundException(f"can't load {resource_path}")

        with open(self.resource_path, 'r',encoding="utf-8_sig") as f:
            max_data = 0
            for line in f.readlines():
                line = line.replace("\n", "").replace(' ','').replace('　','')
                if line == '':
                    continue
                #uma_pt = []
                word_list = line.split(",")
                uma_name = word_list[0]
                points = []
                if len(word_list) > 1:
                    points = list(map(int, word_list[1:]))

                self.uma_pt_dict[uma_name] = points

                if max_data < len(points):
                    max_data = len(points)

        for name in self.uma_pt_dict.keys():
            self.uma_pt_dict[name] += [0 for j in range(max_data-len(self.uma_pt_dict[name]))]

    def WriteUmaList(self):
        with open(self.resource_path, 'w', encoding="utf-8_sig") as f:
            for name, points in self.uma_pt_dict.items():
                f.write(name)
                for data in points:
                    f.write(', ' + str(data))
                f.write('\n')

    def getUmaList(self):
        return sorted(self.uma_pt_dict.keys())

    def addUmaPt(self, read_score:dict):
        for name in self.uma_pt_dict.keys():
            if name in sorted(read_score.keys()):
                self.uma_pt_dict[name].insert(0, read_score[name])
            else:
                self.uma_pt_dict[name].insert(0,0)

    def Max(self):
        def pred(points:np.array):
            if np.any(points > 0):
                return int(np.max(points[points > 0]))
            return 0
        return {name:pred(np.array(points)) for name, points in self.uma_pt_dict.items()}

    def Min(self):
        def pred(points:np.array):
            if np.any(points > 0):
                return int(np.min(points[points > 0]))
            return 0
        return {name:pred(np.array(points)) for name, points in self.uma_pt_dict.items()}

    def Mean(self):
        def pred(points:np.array):
            if np.any(points > 0):
                return int(np.mean(points[points > 0]))
            return 0
        return {name:pred(np.array(points)) for name, points in self.uma_pt_dict.items()}

    def Std(self):
        def pred(points:np.array):
            if np.any(points > 0):
                return int(np.std(points[points > 0]))
            return 0
        return {name:pred(np.array(points)) for name, points in self.uma_pt_dict.items()}

    def len(self):
        return len(self.uma_pt_dict)

    def Metrics(self):
        max_dict = self.Max()
        min_dict = self.Min()
        mean_dict = self.Mean()
        std_dict = self.Std()
        name_list = max_dict.keys()

        return {name:{'max':max_dict[name],
                    'min':min_dict[name],
                    'mean':mean_dict[name],
                    'std':std_dict[name],
                    }
                for name in name_list}

if __name__ == "__main__":
    uma_list = UmaList()
    print(uma_list.getUmaList())        self.name = name
        self.points = points

    @property
    def Max(self) -> int:
        points = np.array(self.points)
        if np.any(points > 0):

        points = np.array(self.points)
        if np.any(points > 0):

    @property
    def Mean(self) -> int:
        points = np.array(self.points)
        if np.any(points > 0):
            return int(np.mean(points[points > 0]))
        return 0

    @property
    def Std(self) -> int:
        points = np.array(self.points)

    def __getitem__(self, key: str):
        item_list = ['Name'] + self.metrics_name_list
        if key not in item_list:
        return {name: metrics
                for name, metrics in zip(item_list, [self.name, self.Max,
                                                     self.Min, self.Mean,
                                                     self.Std])}[key]
class UmaInfoDict(UserDict):
    def __init__(self, __list: List[UmaInfo] = None) -> None:
        super().__init__(__dict)

    def add(self, uma_info: UmaInfo):
        with open(UmaPointFileIO.resource_path, 'w', encoding="utf-8_sig") as f:
            json.dump(
                {uma_info.name: uma_info.points
                 for uma_info in uma_info_dict.values()}, f, indent=2,
                ensure_ascii=False)


