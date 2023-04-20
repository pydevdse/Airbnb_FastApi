from pprint import pprint
from datetime import datetime
from random import randint
import base64
from time import sleep
import json
import requests
from get_headers import get_headers
from params_list_airbnb import params_list
from params_room import params_room
from firefox_ua import USER_AGENT
import pymongo


class AirbnbMongoDB:
    def __init__(self, db_name):
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient[db_name]
        self.room = mydb["room"]

    def get_item(self, itemid):
        item = self.room.find_one({"roomID":itemid})
        
        if item:
            print(f"Found ID:{item['roomID']} User:{item['UserID']} - {itemid}")
            return True
        return

    def save_item(self, item):
        print("Item to DB:", item.get("roomID"))
        if not self.room.find_one({"roomID": item['data']['presentation']['stayProductDetailPage']['sections']['metadata']['loggingContext']['eventDataLogging']['listingId']}):
            result = self.room.insert_one(item)
            print("Item save to DB", result)
            print("Items count in DB:", self.items_count())
            return
        print("Already exist in DB")
        return

    def items_count(self):
        return self.room.count_documents({})

class Airbnb:
    def __init__(self, region="Italy"):
        # self.db = AirbnbMongoDB(region)
        params_list['variables']['staysSearchRequest']['rawParams'][10]['filterValues'] = [region]
        # pprint(json.dumps(params_list['variables']['staysSearchRequest']['rawParams']))

    def sleep(self):
        sleep(randint(7,10))

    def get_room_available(self, room_id, month=None,from_date=None, to_date=None, ): # datetime.now().month):
        headers = get_headers("headers_room.txt")
        url = 'https://www.airbnb.com/api/v3/PdpAvailabilityCalendar?operationName=PdpAvailabilityCalendar&locale=en&' \
              'currency=USD&variables={"request":{"count":12,"listingId":"' + str(room_id) + '","month":' + str(month) + ',"year":2023}}&' \
              'extensions={"persistedQuery":{"version":1,"sha256Hash":"8f08e03c7bd16fcad3c92a3592c19a8b559a0d0855a84028d1163d4733ed9ade"}}'
        print(url)
        try:
            response = requests.get(url, headers=headers) #, params=params_room)
            j = response.json()
        except Exception as e:
            print(e)
            return
        return j

    def get_room_info_price(self, room_id):
        room_id_stay = f"StayListing:{room_id}"
        message_bytes = room_id_stay.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        room_id_base64 = base64_bytes.decode("ascii")
        headers = get_headers("headers_room.txt")
        # headers['user-agent'] = USER_AGENT[randint(0, len(USER_AGENT)-1)]
        # print(headers)
        url = 'https://www.airbnb.com/api/v3/StaysPdpSections?operationName=StaysPdpSections&locale=en&currency=USD&' \
              'variables={"id":"'+ room_id_base64 + '","pdpSectionsRequest":{"adults":"1","bypassTargetings":false,' \
              '"categoryTag":"Tag:8536","causeId":null,"children":"0","disasterId":null,"discountedGuestFeeVersion":null,' \
              '"displayExtensions":null,"federatedSearchId":"ca2ff94b-116f-4bac-89e6-2b7ecb37115b",' \
                '"forceBoostPriorityMessageType":null,"infants":"0","interactionType":null,' \
                '"layouts":["SIDEBAR","SINGLE_COLUMN"],"pets":0,"pdpTypeOverride":null,"preview":false,' \
                '"previousStateCheckIn":null,"previousStateCheckOut":null,"priceDropSource":null,"privateBooking":false,' \
                '"promotionUuid":null,"relaxedAmenityIds":null,"searchId":null,"selectedCancellationPolicyId":null,' \
                '"selectedRatePlanId":null,"splitStays":null,"staysBookingMigrationEnabled":false,"translateUgc":null,' \
                '"useNewSectionWrapperApi":false,"sectionIds":["CANCELLATION_POLICY_PICKER_MODAL",' \
                '"BOOK_IT_CALENDAR_SHEET","POLICIES_DEFAULT","BOOK_IT_SIDEBAR","URGENCY_COMMITMENT_SIDEBAR",' \
                '"BOOK_IT_NAV","BOOK_IT_FLOATING_FOOTER","EDUCATION_FOOTER_BANNER","URGENCY_COMMITMENT",' \
                '"EDUCATION_FOOTER_BANNER_MODAL"],"checkIn":"2023-04-20","checkOut":"2023-04-27",' \
                '"p3ImpressionId":"p3_1681956696_C/HkFitC9INbdHlN","photoId":null}}&extensions={"persistedQuery":' \
                '{"version":1,"sha256Hash":"3aebb59d292ede4bb8fa8b61528d50b5f55fcf40cae4034fc09e0b632ca9fbb8"}}'
        try:
            response = requests.get(url, headers=headers) #, params=params_room)
            j = response.json()
        except Exception as e:
            print(e)
            return
        with open(f"room_info_{room_id}.json", "w") as f:
            json.dump(j, f, ensure_ascii=False, indent=4)

        return j


    def get_room_info(self, room_id):
        room_id_stay = f"StayListing:{room_id}"
        message_bytes = room_id_stay.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        room_id_base64 = base64_bytes.decode("ascii")
        headers = get_headers("headers_room.txt")
        # headers['user-agent'] = USER_AGENT[randint(0, len(USER_AGENT)-1)]
        # print(headers)
        url = 'https://www.airbnb.com/api/v3/StaysPdpSections?operationName=StaysPdpSections&locale=en&' \
              'currency=USD&variables={"id":"'+ room_id_base64 +'","pdpSectionsRequest":' \
              '{"adults":"1","bypassTargetings":false,"categoryTag":null,"causeId":null,"children":null,' \
              '"disasterId":null,"discountedGuestFeeVersion":null,"displayExtensions":null,' \
              '"federatedSearchId":null,"forceBoostPriorityMessageType":null,"infants":null,"interactionType":null,' \
              '"layouts":["SIDEBAR","SINGLE_COLUMN"],"pets":0,"pdpTypeOverride":null,"preview":false,' \
              '"previousStateCheckIn":null,"previousStateCheckOut":null,"priceDropSource":null,' \
              '"privateBooking":false,"promotionUuid":null,"relaxedAmenityIds":null,"searchId":null,' \
              '"selectedCancellationPolicyId":null,"selectedRatePlanId":null,"splitStays":null,' \
              '"staysBookingMigrationEnabled":false,"translateUgc":null,"useNewSectionWrapperApi":false,' \
              '"sectionIds":null,"checkIn":null,"checkOut":null,"photoId":null}}&extensions={"persistedQuery":' \
              '{"version":1,"sha256Hash":"de0455d02d6997f1cebe679cf68bca612af28910bed3b7d5d16976201f7b0241"}}'
        try:
            response = requests.get(url, headers=headers) #, params=params_room)
            j = response.json()
        except Exception as e:
            print(e)
            return
        with open(f"room_info_{room_id}.json", "w") as f:
            json.dump(j, f, ensure_ascii=False, indent=4)

        # j.update({"roomID": j['data']['presentation']['stayProductDetailPage']['sections']['metadata']['loggingContext']['eventDataLogging']['listingId']})
        # userid = j['data']['presentation']['stayProductDetailPage']['sections']['sections']
        # for i in userid:
        #     if i.get('section'):
        #         if i.get('section').get('hostAvatar'):
        #             if i.get('section').get('hostAvatar').get('userId'):
        #                 user_id = i['section']['hostAvatar']['userId']
        # j.update({"UserID":user_id})
        # self.db.save_item(j)

        return j

    def get_items(self, page):
        url = "https://www.airbnb.com/api/v3/StaysSearch?operationName=StaysSearch&locale=en&currency=USD"
        cursor = (
            '{"section_offset":2,"items_offset":' + str(page * 18) + ',"version":1}'
        )
        message_bytes = cursor.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        base64_curcor = base64_bytes.decode("ascii")
        params_list["variables"]["staysSearchRequest"]["cursor"] = base64_curcor
        headers = get_headers("headers_pagin.txt") # ['user-agent'] = USER_AGENT[randint(0, len(USER_AGENT)-1)]
        try:
            response = requests.post(
                url, json=params_list, headers=headers  # get_headers("headers_pagin.txt")
            )
            j = response.json()
        except Exception as e:
            print(e)
            return
        # print(response)
        if response.status_code != 200:
            return
        return response.json()

    def room_user_id(self, room_id):
        params_room["variables"]["request"]["listingId"] = room_id
        url = 'https://www.airbnb.com/api/v3/PdpReviews?operationName=PdpReviews&locale=en&currency=USD&variables=' \
              '{"request":{"fieldSelector":"for_p3_translation_only","limit":7,"listingId":"' + str(room_id) + \
              '","checkinDate":"","checkoutDate":"","numberOfAdults":"1","numberOfChildren":"0","numberOfInfants":"0"}}&extensions={"persistedQuery":{"version":1,"sha256Hash":"6a71d7bc44d1f4f16cced238325ced8a93e08ea901270a3f242fd29ff02e8a3a"}}'
        headers = get_headers("headers_room.txt") #['user-agent'] = USER_AGENT[randint(0, len(USER_AGENT) - 1)]
        try:
            response = requests.get(
                url, headers=headers)
            j = response.json()
        except Exception as e:
            print(e)
            return

        return j

    def user_listing(self, user_id, limit=40, offset=10):
        url = f'https://www.airbnb.com/api/v2/user_promo_listings?locale=en&currency=USD&_limit={limit}&_offset={0}' \
              f'&user_id={user_id}'
        headers = get_headers("headers_room.txt") #['user-agent'] = USER_AGENT[randint(0, len(USER_AGENT) - 1)]
        try:
            response = requests.get(url, headers=headers)
            j = response.json()
        except Exception as e:
            print(e)
            return
        record_count = j["metadata"]["record_count"]

        print('record_count:', record_count)
        if limit<record_count:
            self.sleep()
            j = self.user_listing(user_id, record_count) #, record_count)

        # with open(f"user_listing-{user_id}.json", "w") as f:
        #     json.dump(j, f, ensure_ascii=False, indent=4)
        return j

    def user_info(self, user_id):
        url = 'https://www.airbnb.com/api/v3/GetConsentForUserQuery?operationName=GetConsentForUserQuery&locale=en&currency=USA&variables={"deviceId":"1676999524_MjE4MzJiMDA3MTQz","consentId":null,"includeConfigView":true}&extensions={"persistedQuery":{"version":1,"sha256Hash":"805bdcc4937dee31c2d53ae88f400d42c6637915a2cafc73f0b30a61c9ffda73"}}'
        print(j)
        with open("user_airbnb.json", "w") as f:
            json.dump(json.loads(j[0]), f, ensure_ascii=False, indent=4)

    def main(self, pages):
        items = []
        for page in range(1, pages + 1):
            print(f"page: {page}  ---------------------------------------------------")
            self.sleep()
            response = self.get_items(page)
            if response is None:
                return
            j = response["data"]["presentation"]["explore"]["sections"][
                "sectionIndependentData"
            ]["staysSearch"]["searchResults"]
            print(f"Items on page {page}:", len(j))
            items.append(j)
            for item in j:

                print("item:", item['listing']['id'])
                if self.db.get_item(item['listing']['id']):
                    print("Already exist main")
                    continue
                self.sleep()
                userid = self.get_room_info(item['listing']['id'])
                userid = userid['data']['presentation']['stayProductDetailPage']['sections']['sections']
                for i in userid:
                    if i.get('section'):
                        if i.get('section').get('hostAvatar'):
                            if i.get('section').get('hostAvatar').get('userId'):
                                user_id = i['section']['hostAvatar']['userId']
                self.sleep()
                print("User ID:", user_id)
                user_list = self.user_listing(user_id)["user_promo_listings"]

                print("user listing:", len(user_list))
                #print(user_list)
                for l in user_list:
                    print(f"Item in user:{user_id} listing:", l['id'])
                    if self.db.get_item(l['id']):
                        print("Already exist main")
                        continue
                    self.sleep()
                    item_info = self.get_room_info(l['id'])
        #with open("Italy.json", "w") as f:
        #    json.dump(items, f, indent=4)  # ensure_ascii=False,


if __name__ == "__main__":
    print(Airbnb().get_room_info(593366110540588381))
    #Airbnb().room_user_id(40012920)
    #
    # Airbnb(region="Greece").main(15)
    #Airbnb().user_listing(29037039) # 163663206
