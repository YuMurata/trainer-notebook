from uma_info import UmaNameFileReader, UmaPointFileIO

if __name__ == '__main__':
    print(UmaNameFileReader.Read())
    uma_info_dict = UmaPointFileIO.Read()
    print(uma_info_dict)
    print(list(uma_info_dict.values())[0].scores.mean)
