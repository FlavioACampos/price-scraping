from datetime import datetime, UTC
from scrapy import Spider, Request


class AmazonSpider(Spider):
    """Sends requests for https://amazon.com products and gets their price and availability back."""

    name = "amazon"
    allowed_domains = ["amazon.com"]

    def __init__(self):
        url_list = [
            # TODO: Remove once the spider is set to run as a script
            "https://www.amazon.com/dp/0345816021"
        ]
        self.url_list = url_list

    def is_product_url(self, url):
        # Correct URL examples:
        # https://www.amazon.com/dp/0345816021
        # https://www.amazon.com/12-Rules-Life-Antidote-Chaos/dp/0141988517
        if "/dp/" in url:
            return True
        self.logger.warning("Invalid URL found for Amazon '%s'", url)
        return False

    def start_requests(self):
        for url in self.url_list:
            url = url.split("?")[0]
            prod_id = url.split("/dp/")[-1].split("/")[0]
            yield Request(
                url,
                headers={
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "accept-language": "en-US,en;q=0.9,es-MX;q=0.8,es-US;q=0.7,es;q=0.6",
                    "referer": "https://www.amazon.com",
                },
                dont_filter=True,
                meta={"base_url": url, "id": prod_id},
                callback=self.parse,
            )

    def parse(self, response):
        """Tries to parse the response into JSON,
        extracts the required data from it, and yields it in a dictionary.
        """
        item = {}
        id = response.meta.get("id")
        item["id"] = id
        item["url"] = response.meta.get("base_url")
        item["extraction_date"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M")
        item["response_url"] = response.url
        try:
            price = response.css("#twister-plus-price-data-price::attr(value)").get()
            float_price = float(price.replace(",", "").replace("$", ""))
            # TODO: Amazon has multiple prices per product (different sellers)
            # Right now we grab the default, but it could be a good idea to grab all prices.
            item["price"] = float_price
            in_stock = response.css("#availability > span::Text").get("")
            in_stock = in_stock.strip().lower() == "in stock"
            item["is_not_available"] = False if in_stock else True
            item["is_out_of_stock"] = False if in_stock else True
        except:
            self.logger.error("An exception ocurred while scraping the data.")
        yield item
