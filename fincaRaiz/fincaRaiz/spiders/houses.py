from scrapy_playwright.page import PageMethod
from ..itemsloaders import FincaraizItemLoader
from scrapy.selector import Selector
from ..items import FincaraizItem
import scrapy


class HousesSpider(scrapy.Spider):
    name = "houses"

    def start_requests(self):
        regions = [{"city": "medellin", "state": "antioquia"}]
        for region in regions:
            city = region["city"]
            state = region["state"]
            yield scrapy.Request(
                url=f"https://www.fincaraiz.com.co/apartamentos-casas/arriendos/{city}/{state}?pagina=1",
                callback=self.parse_pages,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "domcontentloaded"),
                    ],
                    "city": city,
                    "state": state,
                    "page_number": 1,
                },
                errback=self.close_page,
            )

    async def parse_pages(self, response):
        page = response.meta["playwright_page"]

        await page.wait_for_selector(".MuiPaper-root")
        content = Selector(text=await page.content())
        await page.close()

        houses = content.css("article.MuiPaper-root")
        for article in houses:
            yield scrapy.Request(
                url="https://www.fincaraiz.com.co"
                + article.xpath(
                    ".//a[contains(@class, 'MuiTypography-root')]/@href"
                ).get(),
                callback=self.parse_house,
                meta={
                    "price": article.xpath(
                        ".//a/div/section/div[1]/span[1]/b/text()"
                    ).get()
                },
            )

        # total houses:
        # total_houses = content.xpath(
        #     "//h1[contains(@class, 'MuiTypography-h5')]/text()"
        # ).get()
        # total_houses = total_houses.split(" ")[0]
        # total_pages = int(total_houses.replace(".", "")) / 25
        # if total_pages - int(total_pages) != 0:
        #     total_pages = int(total_pages) + 1

        city = response.meta["city"]
        state = response.meta["state"]
        page_number = response.meta["page_number"]
        if page_number < 41:  # Viewable pages
            yield scrapy.Request(
                url=f"https://www.fincaraiz.com.co/apartamentos/arriendos/{city}/{state}?pagina={page_number+ 1}",
                callback=self.parse_pages,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "domcontentloaded"),
                    ],
                    "city": city,
                    "state": state,
                    "page_number": page_number + 1,
                },
                errback=self.close_page,
            )

    def parse_house(self, response):
        xpath = "//div[contains(@class, 'jss252')]"
        if len(response.xpath(xpath + "/div")) == 2:
            xpath = xpath + "/div[1]"

        parking = False
        if response.xpath(xpath + "/div[3]/div[2]/p[1]/text()").get() == "Parqueaderos":
            parking = True
        area = response.xpath(xpath + "/div[3]/div[2]/p[2]/text()").get()
        if (
            response.xpath(xpath + "/div[3]/div[2]/p[1]/text()").get()
            != "Área construída"
        ):
            area = response.xpath(xpath + "/div[4]/div[2]/p[2]/text()").get()
        stratum = response.xpath(xpath + "/div[5]/div[2]/p[2]/text()").get()
        if response.xpath(xpath + "/div[5]/div[2]/p[1]/text()").get() != "Estrato":
            stratum = response.xpath(xpath + "/div[6]/div[2]/p[2]/text()").get()

        house = FincaraizItemLoader(FincaraizItem(), response)
        house.add_xpath("rooms", xpath + "/div[1]/div[2]/p[2]/text()")
        house.add_xpath("bathrooms", xpath + "/div[2]/div[2]/p[2]/text()")
        house.add_value("parking", parking)
        house.add_value("area", area)
        house.add_value("stratum", stratum)
        house.add_value("price", response.meta["price"])
        yield house.load_item()

    async def close_page(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
