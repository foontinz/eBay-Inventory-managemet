import time
from main import DataBaseInterface
from ebay_utils import refresh_token, set_item_quantity
from scrape_frameworks import Scraper

db = DataBaseInterface()
scrape_core = Scraper()

websites = {
    "https://www.amazon.co.jp/": lambda x, y: scrape_core.scrape_amazon(link=x, stock_word=y),
    "https://page.auctions.yahoo.co.jp/jp/": lambda x, y: scrape_core.scraper_yahoo(link=x, stock_word=y),
    "https://jp.mercari.com/item/": lambda x, y: scrape_core.scraper_mercari(link=x, stock_word=y),
    "https://item.fril.jp/": lambda x, y: scrape_core.scraper_item_fril(link=x, stock_word=y),
    "https://paypayfleamarket.yahoo.co.jp/ite": lambda x, y: scrape_core.scraper_paypay_flea_market_yahoo(link=x,
                                                                                                          stock_word=y),
    "https://www.suruga-ya.jp/product/detail/": lambda x, y: scrape_core.scraper_suruga_ya(link=x, stock_word=y),
    "https://netmall.hardoff.co.jp/product/": lambda x, y: scrape_core.scraper_hardoff(link=x, stock_word=y),
    "https://order.mandarake.co.jp/order/detailPage/item": lambda x, y: scrape_core.scraper_mandarake(link=x,
                                                                                                      stock_word=y),
    "https://shop.lashinbang.com/products/detail/": lambda x, y: scrape_core.scraper_lashinbang(link=x, stock_word=y),
    "https://paypaymall.yahoo.co.jp/store": lambda x, y: scrape_core.scraper_paypaymall_yahoo(link=x, stock_word=y),
    "https://www.kosho.or.jp/products/": lambda x, y: scrape_core.scraper_kosho(link=x, stock_word=y),
    "https://item.rakuten.co.jp": lambda x, y: scrape_core.scraper_rakuten(link=x, stock_word=y)
}

while True:
    cur_time = time.time()
    for product in db.get_all_products():
        if product[19]:
            result = product[20]
            ebay_qt = product[18]
            ebay_id = product[2]
            ecommerce_url = product[3]
            stock_word = product[8]
            user_id = product[0]

            current_time = int(time.time())

            availability, price = websites[
                f"{''.join(key for key in websites.keys() if ecommerce_url.startswith(key))}"](
                ecommerce_url, stock_word)

            db.edit_p_price_by_ebay_id(ebay_id, price if price != '0' else product[5])
            db.edit_availability_by_ebay_id(ebay_id, availability)

            token = refresh_token(db.get_token_by_user_id(user_id))
            if (not availability) and product[17] == '1' and token != '0' and result == '1':
                set_item_quantity(ebay_id, 0, token)
            if availability and product[17] == '1' and token != '0' and result == '0':
                set_item_quantity(ebay_id, ebay_qt, token)
            time.sleep(5)
    time.sleep(cur_time + 43200 - time.time())
