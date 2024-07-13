import json


def cookies_to_dict():
    """Creates cookies in a python dict format from a json cookies file.
    The json cookie file is generated for any chrome tab using a the following extension:
    https://chromewebstore.google.com/detail/copy-cookies/jcbpglbplpblnagieibnemmkiamekcdg
    """
    result_dict = {}

    with open(".tmp/cookies.json", "r") as c:
        list_of_cookies = json.loads(c.read())

    for item in list_of_cookies:
        result_dict[item["name"]] = item["value"]

    with open("scrapy_cookies.json", "w") as f:
        f.write(json.dumps(result_dict))


if __name__ == "__main__":
    cookies_to_dict()
