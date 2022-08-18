import pprint
import time

import requests
import base64
import bs4


def refresh_token(auth_code):
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


def set_item_quantity(ebay_id,quantity, token):
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

