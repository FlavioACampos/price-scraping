from datetime import datetime, UTC
import json
from scrapy import Spider, Request


class LowesSpider(Spider):
    """Sends requests for https://lowes.com products and gets their price and availability back."""

    name = "lowes"
    allowed_domains = ["lowes.com"]
    custom_settings = {"LOG_LEVEL": "DEBUG"}  # Temporary

    def is_product_url(self, url):
        split_url = url.split("/")
        # Correct URL example: https://www.lowes.com/pd/product_name/5013537917
        if "/pd/" in url and len(split_url) == 6 and split_url[-1].isdigit():
            return True
        self.logger.warning("Invalid URL found for Lowes '%s'", url)
        return False

    def __init__(self):
        url_list = [
            # TODO: Remove once the spider is set to run as a script
            "https://www.lowes.com/pd/Frigidaire-25-6-cu-ft-Side-by-Side-Refrigerator-with-Ice-Maker-Easycare-Stainless-Steel-ENERGY-STAR/5013537917"
        ]
        self.url_list = url_list
        self.store_number = "1013"

    def set_request(self, url):
        sku = url.split("?")[0].split("/")[-1]
        return Request(
            url="https://www.lowes.com/purchase/api/product/details",
            method="POST",
            headers={
                "abtest": "{}",
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-US,en;q=0.9,es-MX;q=0.8,es-US;q=0.7,es;q=0.6",
                "business-channel": "DIGITAL_LOWESDESKTOP",
                "cache-control": "no-cache",
                "content-type": "application/json",
                "locale": "en-US",
                "origin": "https://www.lowes.com",
                "priority": "u=1, i",
                "referer": "https://www.lowes.com/cart",
                "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-requested-with": "XMLHttpRequest",
                "x-web-app": "true",
            },
            cookies={"sn": self.store_number},
            body=json.dumps(
                {"omniItemIds": [sku], "isQuickView": True, "isCuratedList": False}
            ),
            dont_filter=True,
            meta={"product_url": url},
            callback=self.parse,
        )

    def start_requests(self):
        for url in self.url_list:
            if self.is_product_url(url):
                request = self.set_request(url)
                yield request

    def get_price(self, data):
        price = None
        try:
            pass
        except:
            self.logger.error("An error ocurred while scraping the price.")
        return price

    def get_price(self, data):
        is_available = None
        try:
            pass
        except:
            self.logger.error("An error ocurred while scraping the availability.")
        return is_available

    def parse(self, response):
        """Receives a response and tries to parse into JSON,
        then grabs the price and availability and yields in a dictionary.
        """
        item = {}
        item["extraction_date"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M")
        try:
            data = json.loads(response.text)
            item["product_url"] = response.meta.get("product_url")
            item["price"] = self.get_price(data)
            item["IsAvailable"] = self.get_availability(data)
        except:
            self.logger.error("An error ocurred while scraping the data.")
        return item
