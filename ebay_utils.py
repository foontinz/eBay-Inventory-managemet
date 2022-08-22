import tkinter as tk
import webbrowser
from urllib.parse import unquote
import base64
import requests


class EbayTokenCreation:
    def __init__(self):
        self._refresh_token = '0'
        self.create_token()

    def create_input_window(self):
        self.root = tk.Tk()
        self.root.title("Auth URL")
        self.root.geometry("300x150+10+20")
        label = tk.Label(self.root, text="Input URL after auth", font=("Helvetica", 16))
        label.place(x=40, y=15)
        entry = tk.Entry(self.root)
        entry.place(x=65, y=55)
        btn = tk.Button(self.root, text="Continue", font=("Helvetica", 16),
                        command=lambda: self.send_request_for_token(entry.get().strip()))
        btn.place(x=75, y=85)
        self.root.mainloop()

    def create_token(self):
        auth_url = "https://auth.ebay.com/oauth2/authorize?client_id=DimaYuri-dropship-PRD-f13d8ad47-4b5b8dbd&response_type=code&redirect_uri=Dima_Yurinov-DimaYuri-dropsh-gzgoijo&scope=https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly https://api.ebay.com/oauth/api_scope/sell.finances https://api.ebay.com/oauth/api_scope/sell.payment.dispute https://api.ebay.com/oauth/api_scope/commerce.identity.readonly https://api.ebay.com/oauth/api_scope/commerce.notification.subscription https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly"
        webbrowser.open_new(auth_url)
        self.create_input_window()

    def send_request_for_token(self, auth_res_url):
        start_number = auth_res_url.find('code=') + len('code=')
        end_number = auth_res_url.find('&expires_in')
        auth_code = unquote(auth_res_url[start_number:end_number])
        b64_id_secret = base64.b64encode(
            bytes('DimaYuri-dropship-PRD-f13d8ad47-4b5b8dbd' + ':' + 'PRD-13d8ad478a55-aed0-46f1-b028-06cb',
                  'utf-8')).decode('utf-8')

        response = requests.post("https://api.ebay.com/identity/v1/oauth2/token",
                                 headers={
                                     "Content-Type": "application/x-www-form-urlencoded",
                                     "Authorization": "Basic " + b64_id_secret
                                 },
                                 data={
                                     "grant_type": "authorization_code",
                                     "code": auth_code,
                                     "redirect_uri": 'Dima_Yurinov-DimaYuri-dropsh-gzgoijo'
                                 })
        token = response.json()
        self.refresh_token = token['refresh_token']
        self.root.quit()

    @property
    def refresh_token(self):
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, token):
        self._refresh_token = token

    def __repr__(self):
        return self.refresh_token


def refresh_token(auth_code, attempts=0):
    if attempts < 3:
        attempts += 1
        try:
            b64_id_secret = base64.b64encode(
                bytes('DimaYuri-dropship-PRD-f13d8ad47-4b5b8dbd' + ':' + 'PRD-13d8ad478a55-aed0-46f1-b028-06cb',
                      'utf-8')).decode('utf-8')

            response = requests.post("https://api.ebay.com/identity/v1/oauth2/token",
                                     headers={
                                         "Content-Type": "application/x-www-form-urlencoded",
                                         "Authorization": "Basic " + b64_id_secret
                                     },
                                     data={
                                         "grant_type": "refresh_token",
                                         "refresh_token": auth_code,
                                         "redirect_uri": 'Dima_Yurinov-DimaYuri-dropsh-gzgoijo'
                                     })
            token = response.json()
            return token['access_token']
        except AttributeError or Exception:
            return refresh_token(auth_code, attempts)
    else:
        return '0'


def set_item_quantity(ebay_id, quantity, token):
    headers = {'X-EBAY-API-SITEID': '0',
               'X-EBAY-API-COMPATIBILITY-LEVEL': '967',
               'X-EBAY-API-CALL-NAME': 'ReviseFixedPriceItem',
               'X-EBAY-API-IAF-TOKEN': f'{token}'}
    xml = f"""
            <?xml version="1.0" encoding="utf-8"?>
    <ReviseFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">    
        <ErrorLanguage>en_US</ErrorLanguage>
        <WarningLevel>High</WarningLevel>
      <Item>
        <!-- Enter the ItemID of the fixed-price listing and the information you want to revise -->
        <ItemID>{ebay_id}</ItemID>
        <Quantity>{quantity}</Quantity>
      </Item>
    </ReviseFixedPriceItemRequest>"""
    requests.post("https://api.ebay.com/ws/api.dll", headers=headers, data=xml)
