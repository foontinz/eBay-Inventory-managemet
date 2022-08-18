import pprint

import bs4
import requests


class Scraper:
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "Accept-Encoding: gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }

    @staticmethod
    def make_soup(html):
        return bs4.BeautifulSoup(html, 'html.parser')

    def make_request(self, link: str, headers, querystring, attempts=0):
        attempts += 1
        if querystring:
            res = requests.get(link, headers=headers, params=querystring)
        else:
            res = requests.get(link, headers=headers)

        if res.status_code == 200 and attempts < 3:
            return res
        else:
            return self.make_request(link, headers, querystring=querystring, attempts=attempts)

    def scrape_amazon(self, link: str, stock_word: str):
        html = self.make_request(link, self.headers, None).text
        soup = self.make_soup(html)

        availability = stock_word in html

        if availability:
            try:
                price = ''.join(filter(str.isdigit, soup.find("span", {"class": "a-price-whole"}).text))
            except AttributeError:
                try:
                    price = ''.join(filter(str.isdigit, soup.find("strong", {"class": "priceLarge"}).text))
                except AttributeError:
                    price = 0
        else:
            price = 0
        return availability, price

    def scraper_yahoo(self, link: str, stock_word: str):
        html = self.make_request(link, self.headers, None).text
        soup = self.make_soup(html)

        availability = stock_word in html
        try:
            price = ''.join(filter(str.isdigit, soup.find("dd", {"class": "Price__value"}).find(text=True)))
        except AttributeError:
            price = '0'
        return availability, price

    def scraper_mercari(self, link: str, stock_word: str):
        headers = {
            "cookie": "merCtx=%22%22",
            "authority": "api.mercari.jp",
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru,en-US;q=0.9,en;q=0.8,uk-UA;q=0.7,uk;q=0.6,ru-RU;q=0.5",
            "dpop": "eyJ0eXAiOiJkcG9wK2p3dCIsImFsZyI6IkVTMjU2IiwiandrIjp7ImNydiI6IlAtMjU2Iiwia3R5IjoiRUMiLCJ4IjoiRjRTbS1xOXA2dUFiQXB1RE9ab0YyTy1BR0RsUWw5REpnTGZZWThhTk10RSIsInkiOiJFTm5RbG5FbjZaZkNwWU5XWXAzR3duWk1TWWhSUko2NVNGNjUxWHdVQno0In19.eyJpYXQiOjE2NjA4MzI5MzgsImp0aSI6ImYzMGY1NjYwLTYzNmEtNDhlNy1iZWVlLWQ5YTEwZTQ5MjhiNCIsImh0dSI6Imh0dHBzOi8vYXBpLm1lcmNhcmkuanAvaXRlbXMvZ2V0IiwiaHRtIjoiR0VUIiwidXVpZCI6ImQ3ZmJkMmRhLTBlZWEtNDgyNS05MDQxLTc5ZDJkMTc2MTNiNSJ9.9__j-5dQ1nMOjY23nWgkQlB2_SobRpRKyN3LO_K4Ks5JQlFbSKlGFkMx-wcWSEGHTybtDszON3OVq6sI_GmmMA",
            "origin": "https://jp.mercari.com",
            "referer": "https://jp.mercari.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "x-platform": "web"
        }
        try:
            querystring = {"id": f"{link[link.rfind('/') + 1:]}"}
            link = 'https://api.mercari.jp/items/get'
            json_dict = self.make_request(link, headers, querystring).json()
            price = json_dict['data']['price']
            availability = json_dict['data']['status'] == 'on_sale'
        except AttributeError or Exception:
            return True, 0
        return availability, price

    def scraper_item_fril(self, link: str, stock_word: str):
        html = self.make_request(link, self.headers, None).text
        soup = self.make_soup(html)

        availability = stock_word in html
        try:
            price = ''.join(filter(str.isdigit, soup.find("span", {"class": "item__value"}).text))
        except AttributeError:
            price = 0
        return availability, price

    def scraper_paypay_flea_market_yahoo(self, link: str, stock_word: str):
        html = self.make_request(link, self.headers, None).text
        soup = self.make_soup(html)

        availability = stock_word in html
        try:
            price = ''.join(
                filter(str.isdigit, soup.find("span", {"class": "sc-f27eb67d-0 euzCBb ItemPrice__Component"}).text))
        except AttributeError:
            price = 0
        return availability, price

    def scraper_store_shopping_yahoo(self, link: str, stock_word: str):
        html = self.make_request(link, self.headers, None).text
        soup = self.make_soup(html)

        availability = stock_word in html
        try:
            price = ''.join(
                filter(str.isdigit, soup.find("span", {"class": "elPriceNumber"}).text))
        except AttributeError:
            price = 0
        return availability, price

    def scraper_suruga_ya(self, link: str, stock_word: str):
        html = self.make_request(link, self.headers, None).text
        soup = self.make_soup(html)

        availability = stock_word in html
        try:
            price = ''.join(
                filter(str.isdigit, soup.find("span", {"class": "text-price-detail price-buy"}).text))
        except AttributeError:
            price = 0
        return availability, price

    def scraper_hardoff(self, link: str, stock_word: str):
        html = self.make_request(link, self.headers, None).text
        soup = self.make_soup(html)

        availability = stock_word in html
        try:
            price = ''.join(
                filter(str.isdigit, soup.find("span", {"class": "product-detail-price__main"}).text))
        except AttributeError:
            price = 0
        return availability, price

    def scraper_mandarake(self, link: str, stock_word: str):
        html = self.make_request(link, self.headers, None).text
        soup = self.make_soup(html)

        availability = stock_word in html
        try:
            price = ''.join(filter(str.isdigit, soup.find("meta", itemprop="price")['content']))
        except AttributeError:
            price = 0
        return availability, price

    def scraper_lashinbang(self, link: str, stock_word: str):
        html = self.make_request(link, self.headers, None).text
        soup = self.make_soup(html)
        availability = False if soup.find("div", {"class": "soldout"}) else True
        try:
            if ''.join(filter(str.isdigit, soup.find("div", {"class": "item_price cf"}).find("p").contents[1])):
                price = ''.join(
                    filter(str.isdigit, soup.find("div", {"class": "item_price cf"}).find("p").contents[1]))
            else:
                price = ''.join(
                    filter(str.isdigit, soup.find("div", {"class": "item_price cf"}).find("p").contents[0]))
        except AttributeError:

            price = 0
        return availability, price

    def scraper_paypaymall_yahoo(self, link: str, stock_word: str):
        html = self.make_request(link, self.headers, None).text
        soup = self.make_soup(html)
        availability = stock_word in html
        try:
            price = ''.join(
                filter(str.isdigit, soup.find("dl", {"class": "ItemPrice_item ItemPrice-selling"}).find("p", {
                    "class": "ItemPrice_price"}).text))
        except AttributeError:

            price = 0
        return availability, price

    def scraper_kosho(self, link: str, stock_word: str):
        html = self.make_request(link, self.headers, None).text
        soup = self.make_soup(html)
        availability = stock_word in html
        try:
            price = ''.join(
                filter(str.isdigit, soup.find("strong", {"class": "red t-price"}).text))
        except AttributeError:

            price = 0
        return availability, price

    def scraper_rakuten(self, link: str, stock_word: str):
        html = self.make_request(link, self.headers, None).text
        soup = self.make_soup(html)
        availability = "outofstock" not in soup.find("meta", itemprop="availability")["content"].lower()
        try:
            price = ''.join(filter(str.isdigit, soup.find("span", {"itemprop": "price"}).text))
        except AttributeError:

            price = 0
        return availability, price

# scrapy = Scraper()
# print(scrapy.scraper_lashinbang("https://shop.lashinbang.com/products/detail/2912770", 'stck'))
