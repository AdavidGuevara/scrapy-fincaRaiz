from itemloaders.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader


class FincaraizItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    price_in = MapCompose(lambda x: x.replace("$", "").replace(".", ""))
    area_in = MapCompose(lambda x: x.replace(" m²", ""))
