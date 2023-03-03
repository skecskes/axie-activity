import requests


class UserItem:
    item_id: str
    quantity: int

    def __init__(self, item_id, quantity):
        self.item_id = item_id
        self.quantity = quantity


class Skymavis:
    _url: str = "https://game-api-origin.skymavis.com/v2"
    _x_api_key: str = "1f598d83-f554-4856-b7f3-cfa8b67f4be1"

    def __init__(self):
        pass

    def get_users_items(self, account: str) -> []:
        path = f"/community/users/items?userID={account}&limit=100&offset="
        url = self._url + path
        headers = {'X-API-Key': self._x_api_key}

        offset = 0
        user_items = []
        while True:
            response = requests.request("GET", url + str(offset), headers=headers)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("_items"):

                    # it even returns zero quantities, so we filter them out
                    quantity = item.get("quantity")
                    if quantity != 0:
                        user_items.append(UserItem(item.get("itemId"), quantity))
                if data.get("_metadata").get("hasNext"):
                    offset = offset + 1
                else:
                    break
            else:
                break

        return user_items
