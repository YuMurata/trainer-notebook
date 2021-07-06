from misc import StopWatch
from TeamStadiumInfoDetection import RankReader
from snip import ImageSnipper
from logger import CustomLogger
logger = CustomLogger(__name__)


def test_read_rank():
    snipper = ImageSnipper()
    reader = RankReader()

    def test():
        with StopWatch('test time', logger):
            snip_image = snipper.Snip()
            logger.info(f'read: {reader.can_read(snip_image)}')
            read_dict = reader.read(snip_image)
            logger.info(f'dict: {read_dict}')
            logger.info(f'read_num: {len(read_dict)}')

    test()
    while input('continue? (y/n) ->') == 'y':
        test()
