import requests
from tinydb import TinyDB, Query
from tinydb import where


class GraphQLService:
    _url: str
    db: TinyDB

    def __init__(self, db):
        self._url = "https://graphql-gateway.axieinfinity.com/graphql"
        self.db = db

    def get_account_by_ronin_address(self, address: str) -> str:
        if not self._valid_address(address):
            raise Exception("Sorry, invalid ronin address")
        address = self._prepare_ronin_address(address)

        payload = "{\"query\":\"query GetProfileByRoninAddress($roninAddress: String!) {\\n  publicProfileWithRoninAddress(roninAddress: $roninAddress) {\\n    ...Profile\\n }\\n}\\n\\nfragment Profile on PublicProfile {\\n  accountId\\n  name\\n}\",\"variables\":{\"roninAddress\":\"" + address + "\"}}"
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", self._url, headers=headers, data=payload)

        if response.status_code == 200:
            return response.json().get('data').get('publicProfileWithRoninAddress').get("accountId")
        else:
            return ""

    def save_recently_items_sold(self):
        headers = {'Content-Type': 'application/json'}
        offset = 0
        size = 100
        while True:

            payload = "{\"query\":\"query GetRecentlyItemsSold($from: Int, $size: Int) {\\n  settledAuctions {\\n    items(from: $from, size: $size) {\\n      total\\n      results {\\n        ...ItemSettledBrief\\n        transferHistory {\\n          ...TransferHistoryInSettledAuction\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment ItemSettledBrief on LandItem {\\n  itemId\\n  name\\n  itemAlias\\n  itemId\\n  figureURL\\n  rarity\\n  __typename\\n}\\n\\nfragment TransferHistoryInSettledAuction on TransferRecords {\\n  total\\n  results {\\n    ...TransferRecordInSettledAuction\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment TransferRecordInSettledAuction on TransferRecord {\\n  from\\n  to\\n  txHash\\n  timestamp\\n  withPrice\\n  withPriceUsd\\n  fromProfile {\\n    name\\n    __typename\\n  }\\n  toProfile {\\n    name\\n    __typename\\n  }\\n  __typename\\n}\",\"variables\":{\"from\":"+str(offset)+",\"size\":"+str(size)+"}}"
            response = requests.request("POST", self._url, headers=headers, data=payload)
            if response.status_code == 200:
                items = response.json().get('data').get('settledAuctions').get('items').get('results')
                if len(items) > 0:
                    for item_sold in items:
                        transfer = item_sold.get('transferHistory').get('results')[0]
                        self.db.insert({
                            'item_id': item_sold.get('itemId'),
                            'name': item_sold.get('name'),
                            'seller': transfer.get('from'),
                            'buyer': transfer.get('to'),
                            'timestamp': transfer.get('timestamp'),
                            'tx_hash': transfer.get('txHash'),
                            'with_price_usd': transfer.get('withPriceUsd')
                        })
                    offset = offset + size
                    print("Saved " + str(offset) + " items")
                else:
                    break
            else:
                break

    def get_activity_of_user(self, ronin_address: str) -> []:
        if not self._valid_address(ronin_address):
            raise Exception("Sorry, invalid ronin address")
        address = self._prepare_ronin_address(ronin_address)
        sales_from_db = self.db.search((where('seller') == address) | (where('buyer') == address))
        return  sales_from_db

    @staticmethod
    def _valid_address(address: str) -> bool:
        length = len(address)
        return address.startswith("ronin:") and 46 == length

    @staticmethod
    def _prepare_ronin_address(address: str) -> str:
        (prefix, the_rest) = address.split("ronin:")
        return "0x" + the_rest
