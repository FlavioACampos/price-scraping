from scrapy import Request

url = "https://www.lowes.com/wpd/5014168851/productdetail/1539/Guest/82001?nearByStore=1539&zipState=WY"

request = Request(
    url=url,
    method="GET",
    dont_filter=True,
    cookies={
        "dbidv2": "6b40d1bc-f49d-40ea-bc17-f416abeb4e80",
        "EPID": "6b40d1bc-f49d-40ea-bc17-f416abeb4e80",
        "sn": "1955",
        "zipcode": "55441",
        "nearbyid": "1955",
        "zipstate": "MN",
        "region": "central",
        # URL encoded json cookies
        "sd": "%7B%22id%22%3A%221955%22%2C%22zip%22%3A%2255447%22%2C%22city%22%3A%22Plymouth%22%2C%22state%22%3A%22MN%22%2C%22name%22%3A%22Plymouth%20Lowe's%22%2C%22region%22%3A%2212%22%7D",
        "p13n": "%7B%22zipCode%22%3A%2255447%22%2C%22storeId%22%3A%221955%22%2C%22state%22%3A%22MN%22%2C%22audienceList%22%3A%5B%5D%7D",
    },
)
