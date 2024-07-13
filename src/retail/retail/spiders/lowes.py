from urllib.parse import quote
from datetime import datetime, UTC
import json
from scrapy import Spider, Request
from box import Box


class LowesSpider(Spider):
    """Sends requests for https://lowes.com products and gets their price and availability back."""

    name = "lowes"
    allowed_domains = ["lowes.com"]

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
        self.dbidv2 = "6b40d1bc-f49d-40ea-bc17-f416abeb4e80"
        self.store_data = {
            "id": "1539",
            "zip": "82009",
            "city": "Cheyenne",
            "state": "WY",
            "name": "Cheyenne Lowe's",
            "region": "14",
        }
        self.sn = self.store_data["id"]
        self.zip = self.store_data["zip"]
        # user values
        self.user_zip_code = "82001"
        self.user_zip_state = "WY"

    def set_cookies(self):
        p13n = {
            "zipCode": self.zip,
            "storeId": self.sn,
            "state": self.store_data["state"],
            "audienceList": [],
        }
        cookies = {
            "dbidv2": self.dbidv2,
            "EPID": self.dbidv2,
            "sd": quote(json.dumps(self.store_data)),
            "sn": "1539",
            "zipcode": self.zip,
            "zipstate": self.store_data["state"],
            "nearbyid": self.sn,
            "p13n": quote(json.dumps(p13n)),
            "region": "central",
        }
        return cookies

    def start_requests(self):
        querystring = f"?nearByStore={self.sn}&zipState={self.user_zip_state}"
        for url in self.url_list:
            if self.is_product_url(url):
                prod_id = url.split("?")[0].split("/")[-1]
                url = f"https://www.lowes.com/wpd/{prod_id}/productdetail/{self.sn}/Guest/{self.user_zip_code}"
                yield Request(
                    url + querystring,
                    dont_filter=True,
                    cookies=self.set_cookies(),
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
            json_data = json.loads(response.text)
            product = Box(json_data, default_box=True, default_value=None)
            pd = product.productDetails[id]
            if pd:
                item["price"] = pd.location.price.pricingDataList[0].finalPrice
                item["is_not_available"] = pd.product.isArchived
                item["is_out_of_stock"] = pd.product.isOOS
        except:
            self.logger.error("An exception ocurred while scraping the data.")
        yield item
