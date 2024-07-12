from datetime import datetime, UTC
import json
from scrapy import Spider, Request
from box import Box


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
        self.store_number = "1955"
        self.zip_code = "55441"
        self.zip_state = "MN"

    def start_requests(self):
        for url in self.url_list:
            if self.is_product_url(url):
                # TODO: Use a different request because availability values are not reliable
                prod_id = url.split("?")[0].split("/")[-1]
                req_url = f"https://www.lowes.com/wpd/pvs/v3/{prod_id}/{self.store_number}/Guest"
                req_url += f"?items={prod_id}&zipCode={self.zip_code}&zipState={self.zip_state}&nearByStore={self.store_number}"
                yield Request(
                    req_url,
                    headers={
                        "accept": "application/json, text/plain, */*",
                        "accept-language": "en-US",
                        "referer": url,
                    },
                    dont_filter=True,
                    meta={"base_url": url, "product_id": prod_id},
                    callback=self.parse,
                )

    def parse(self, response):
        """Tries to parse the response into JSON,
        extracts the required data from it, and yields it in a dictionary.
        """
        item = {}
        prod_id = response.meta.get("product_id")
        item["status"] = "InProgress"
        item["product_id"] = prod_id
        item["product_url"] = response.meta.get("base_url")
        item["extraction_date"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M")
        try:
            json_data = json.loads(response.text)
            product = Box(json_data, default_box=True, default_value=None)
            mfe = product[prod_id].mfePrice
            item["price"] = mfe.price.additionalData.sellingPrice if mfe else None
            item["is_not_available"] = bool(product[prod_id].isNotAvailable)
            item["is_out_of_stock"] = bool(product[prod_id].isOOS)
            item["status"] = "Success"
        except:
            item["status"] = "Failed"
            self.logger.error("An exception ocurred while scraping the data.")
        yield item
