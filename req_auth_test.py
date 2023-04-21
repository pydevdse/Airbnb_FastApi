from time import sleep
from datetime import datetime, date
import requests


class GetAirbnb():
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_api_token(self):
        us_pa = {"username":self.username, "password":"secret"}
        url_token = "http://192.168.31.90:8080/token"
        try:
            get_auth = requests.post(url_token, data=us_pa)

            token = get_auth.json().get("access_token")
            print(token)
            if token is None:
                print("token not found")
                return
        except Exception as e:
            print("Exception:", e)
            return

        return token

    def get_me(self, token):
        url_me = "http://192.168.31.90:8080/users/me/items/"
        me = requests.get(url_me, headers={"Authorization": f"Bearer {token}"})
        print(me.json())
        return

    def get_item_info(self, token, item_id):
        url_info = f"http://192.168.31.90:8080/item_info/{item_id}"
        #params = {"item_id": item_id}
        headers = {"Authorization": f"Bearer {token}"}
        print(headers)
        response = requests.get(url_info,  headers=headers)
        print(response.json())
        print(response.url)

    def get_item_price(self, token, item_id, checkIn=None, checkOut=None):
        url_price = f"http://192.168.31.90:8080/item_info_price/{item_id}"
        params = {"item_id": item_id, "checkIn": str(checkIn), "checkOut": str(checkOut)}
        response = requests.get(url_price, params=params, headers={"Authorization": f"Bearer {token}"})
        print(response.json())

    def main(self):
        item_list = [50609929, 23322087, 50304771, 6497918]
        token = self.get_api_token()
        if token is None:
            print("Token error")
            return
        for r in range(4):
            sleep(1)
            self.get_me(token)
            self.get_item_info(token, item_id=item_list[r])


if __name__ == '__main__':
    GetAirbnb("johndoe", "secret").main()