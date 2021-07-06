from TeamStadiumInfoDetection import ScoreReader
from snip import ImageSnipper
from logger import CustomLogger
logger = CustomLogger(__name__)


def test_read_score():
    snipper = ImageSnipper()

    def test():
        snip_image = snipper.Snip()
        reader = ScoreReader()
        logger.info(f'read: {reader.can_read(snip_image)}')
        read_dict = reader.read(snip_image)
        logger.info(f'dict: {read_dict}')
        logger.info(f'read_num: {len(read_dict)}')

    test()
    while input('continue? (y/n) ->') == 'y':
        test()
