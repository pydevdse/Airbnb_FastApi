import base64
import json
from datetime import datetime, date
from random import randint
from time import sleep

import pymongo
import requests

from get_headers import get_headers
from params_list_airbnb import params_list
from params_room import params_room


class AirbnbMongoDB:
    def __init__(self, db_name):
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient[db_name]
        self.room = mydb["room"]

    def get_item(self, itemid):
        item = self.room.find_one({"roomID": itemid})

        if item:
            print(f"Found ID:{item['roomID']} User:{item['UserID']} - {itemid}")
            return True
        return

    def save_item(self, item):
        print("Item to DB:", item.get("roomID"))
        if not self.room.find_one(
                {
                    "roomID": item["data"]["presentation"]["stayProductDetailPage"][
                        "sections"
                    ]["metadata"]["loggingContext"]["eventDataLogging"]["listingId"]
                }
        ):
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
        params_list["variables"]["staysSearchRequest"]["rawParams"][10][
            "filterValues"
        ] = [region]
        self.region = region
        # pprint(json.dumps(params_list['variables']['staysSearchRequest']['rawParams']))

    @staticmethod
    def sleep():
        sleep(randint(7, 10))

    def get_room_available(self, room_id, month, from_date=None, to_date=None):  # datetime.now().month):
        headers = get_headers("headers_room.txt")
        url = (
                "https://www.airbnb.com/api/v3/PdpAvailabilityCalendar?operationName=PdpAvailabilityCalendar&locale=en&"
                'currency=USD&variables={"request":{"count":12,"listingId":"'
                + str(room_id)
                + '","month":'
                + str(month)
                + ',"year":2023}}&'
                  'extensions={"persistedQuery":{"version":1,"sha256Hash":"8f08e03c7bd16fcad3c92a3592c19a8b559a0d0855a84028d1163d4733ed9ade"}}'
        )
        # print(url)
        try:
            response = requests.get(url, headers=headers)  # , params=params_room)
            j = response.json()
        except Exception as e:
            print(e)
            return
        return j

    def get_room_info_price(self, room_id, checkIn=None, checkOut=None):
        if checkIn is None:
            d = datetime().now().date()
            checkIn = d
        if checkOut is None:
            d = datetime().now().date()
            checkOut = date(year=d.year, month=d.month, day=d.day + 4)
        room_id_stay = f"StayListing:{room_id}"
        message_bytes = room_id_stay.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        room_id_base64 = base64_bytes.decode("ascii")
        headers = get_headers("headers_room.txt")
        # headers['user-agent'] = USER_AGENT[randint(0, len(USER_AGENT)-1)]
        # print(headers)
        url = (
                "https://www.airbnb.com/api/v3/StaysPdpSections?operationName=StaysPdpSections&locale=en&currency=USD&"
                'variables={"id":"'
                + room_id_base64
                + '","pdpSectionsRequest":{"adults":"1","bypassTargetings":false,'
                  '"categoryTag":"Tag:8536","causeId":null,"children":"0","disasterId":null,"discountedGuestFeeVersion":null,'
                  '"displayExtensions":null,"federatedSearchId":"ca2ff94b-116f-4bac-89e6-2b7ecb37115b",'
                  '"forceBoostPriorityMessageType":null,"infants":"0","interactionType":null,'
                  '"layouts":["SIDEBAR","SINGLE_COLUMN"],"pets":0,"pdpTypeOverride":null,"preview":false,'
                  '"previousStateCheckIn":null,"previousStateCheckOut":null,"priceDropSource":null,"privateBooking":false,'
                  '"promotionUuid":null,"relaxedAmenityIds":null,"searchId":null,"selectedCancellationPolicyId":null,'
                  '"selectedRatePlanId":null,"splitStays":null,"staysBookingMigrationEnabled":false,"translateUgc":null,'
                  '"useNewSectionWrapperApi":false,"sectionIds":["CANCELLATION_POLICY_PICKER_MODAL",'
                  '"BOOK_IT_CALENDAR_SHEET","POLICIES_DEFAULT","BOOK_IT_SIDEBAR","URGENCY_COMMITMENT_SIDEBAR",'
                  '"BOOK_IT_NAV","BOOK_IT_FLOATING_FOOTER","EDUCATION_FOOTER_BANNER","URGENCY_COMMITMENT",'
                  '"EDUCATION_FOOTER_BANNER_MODAL"],"checkIn":"'
                + str(checkIn)
                + '","checkOut":"'
                + str(checkOut)
                + '",'
                  '"p3ImpressionId":"p3_1681956696_C/HkFitC9INbdHlN","photoId":null}}&extensions={"persistedQuery":'
                  '{"version":1,"sha256Hash":"3aebb59d292ede4bb8fa8b61528d50b5f55fcf40cae4034fc09e0b632ca9fbb8"}}'
        )
        try:
            response = requests.get(url, headers=headers)  # , params=params_room)
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
        url = (
                "https://www.airbnb.com/api/v3/StaysPdpSections?operationName=StaysPdpSections&locale=en&"
                'currency=USD&variables={"id":"'
                + room_id_base64
                + '","pdpSectionsRequest":'
                  '{"adults":"1","bypassTargetings":false,"categoryTag":null,"causeId":null,"children":null,'
                  '"disasterId":null,"discountedGuestFeeVersion":null,"displayExtensions":null,'
                  '"federatedSearchId":null,"forceBoostPriorityMessageType":null,"infants":null,"interactionType":null,'
                  '"layouts":["SIDEBAR","SINGLE_COLUMN"],"pets":0,"pdpTypeOverride":null,"preview":false,'
                  '"previousStateCheckIn":null,"previousStateCheckOut":null,"priceDropSource":null,'
                  '"privateBooking":false,"promotionUuid":null,"relaxedAmenityIds":null,"searchId":null,'
                  '"selectedCancellationPolicyId":null,"selectedRatePlanId":null,"splitStays":null,'
                  '"staysBookingMigrationEnabled":false,"translateUgc":null,"useNewSectionWrapperApi":false,'
                  '"sectionIds":null,"checkIn":null,"checkOut":null,"photoId":null}}&extensions={"persistedQuery":'
                  '{"version":1,"sha256Hash":"de0455d02d6997f1cebe679cf68bca612af28910bed3b7d5d16976201f7b0241"}}'
        )
        try:
            response = requests.get(url, headers=headers)  # , params=params_room)
            j = response.json()
        except Exception as e:
            print(e)
            return
        # with open(f"room_info_{room_id}.json", "w") as f:
        #     json.dump(j, f, ensure_ascii=False, indent=4)

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
        # url = "https://www.airbnb.com/api/v3/StaysMapS2Search/ac97d2e72d3fac1b70aec184cd26a77e132a49b76e8b876aa7f436eb60a99354?operationName=StaysMapS2Search&locale=en&currency=USD"
        cursor = (
                '{"section_offset":2,"items_offset":' + str(page * 18) + ',"version":1}'
        )
        message_bytes = cursor.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        base64_curcor = base64_bytes.decode("ascii")
        params_list["variables"]["staysSearchRequest"]["cursor"] = base64_curcor
        headers = get_headers(
            "headers_pagin.txt"
        )  # ['user-agent'] = USER_AGENT[randint(0, len(USER_AGENT)-1)]
        try:
            response = requests.post(url, json=params_list, headers=headers)  # get_headers("headers_pagin.txt") )
            j = response.json()
        except Exception as e:
            print(f"get items {e}, {response.text}")
            return
        # print(response)
        if response.status_code != 200:
            return
        return response.json()

    def room_user_id(self, room_id):
        room_id_stay = f"StayListing:{room_id}"
        message_bytes = room_id_stay.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        room_id_base64 = base64_bytes.decode("ascii")
        print(room_id, room_id_base64)
        url = (
                "https://www.airbnb.com/api/v3/PdpReviews?operationName=PdpReviews&locale=en&currency=USD&variables="
                '{"request":{"fieldSelector":"for_p3_translation_only","limit":7,"listingId":"'
                + str(room_id)
                + '","checkinDate":"","checkoutDate":"","numberOfAdults":"1","numberOfChildren":"0","numberOfInfants":"0"}}&extensions={"persistedQuery":{"version":1,"sha256Hash":"6a71d7bc44d1f4f16cced238325ced8a93e08ea901270a3f242fd29ff02e8a3a"}}'
        )
        # https://www.airbnb.com/api/v3/StaysPdpSections/036017be486462ae7b1e9d9916e4dea14951cf33a75c242b92d267b468d97bfd?operationName=StaysPdpSections&locale=en&currency=USD&variables={"id":"U3RheUxpc3Rpbmc6MjAyNTU0NDc=","pdpSectionsRequest":{"adults":"1","amenityFilters":null,"bypassTargetings":false,"categoryTag":"Tag:8535","causeId":null,"children":"0","disasterId":null,"discountedGuestFeeVersion":null,"displayExtensions":null,"federatedSearchId":"9d6ab2e3-e1fb-4364-933a-ae92906acc41","forceBoostPriorityMessageType":null,"infants":"0","interactionType":null,"layouts":["SIDEBAR","SINGLE_COLUMN"],"pets":0,"pdpTypeOverride":null,"photoId":"1445529823","preview":false,"previousStateCheckIn":null,"previousStateCheckOut":null,"priceDropSource":null,"privateBooking":false,"promotionUuid":null,"relaxedAmenityIds":null,"searchId":null,"selectedCancellationPolicyId":null,"selectedRatePlanId":null,"splitStays":null,"staysBookingMigrationEnabled":false,"translateUgc":null,"useNewSectionWrapperApi":false,"sectionIds":null,"checkIn":"2024-06-03","checkOut":"2024-06-08","p3ImpressionId":"p3_1717073345_vAPEIRA/FjfesQXl"}}&extensions={"persistedQuery":{"version":1,"sha256Hash":"036017be486462ae7b1e9d9916e4dea14951cf33a75c242b92d267b468d97bfd"}}
        url = ('https://www.airbnb.com/api/v3/StaysPdpSections/?operationName=StaysPdpSections&locale=en&currency=USD&variables={"id":"'
               + room_id_base64 + '","pdpSectionsRequest":{"adults":"1","amenityFilters":null,"bypassTargetings":false,"categoryTag":"Tag:8535","causeId":null,"children":"0","disasterId":null,"discountedGuestFeeVersion":null,"displayExtensions":null,"federatedSearchId":"9d6ab2e3-e1fb-4364-933a-ae92906acc41","forceBoostPriorityMessageType":null,"infants":"0","interactionType":null,"layouts":["SIDEBAR","SINGLE_COLUMN"],"pets":0,"pdpTypeOverride":null,"photoId":"1445529823","preview":false,"previousStateCheckIn":null,"previousStateCheckOut":null,"priceDropSource":null,"privateBooking":false,"promotionUuid":null,"relaxedAmenityIds":null,"searchId":null,"selectedCancellationPolicyId":null,"selectedRatePlanId":null,"splitStays":null,"staysBookingMigrationEnabled":false,"translateUgc":null,"useNewSectionWrapperApi":false,"sectionIds":null,"checkIn":"2024-06-03","checkOut":"2024-06-08","p3ImpressionId":"p3_1717073345_vAPEIRA/FjfesQXl"}}&extensions={"persistedQuery":{"version":1,"sha256Hash":"036017be486462ae7b1e9d9916e4dea14951cf33a75c242b92d267b468d97bfd"}}')
        headers = get_headers(
            "headers_user.txt"
        )  # ['user-agent'] = USER_AGENT[randint(0, len(USER_AGENT) - 1)]
        try:
            response = requests.get(url, headers=headers)
            j = response.json()
        except Exception as e:
            print(e)
            return
        # user_id = j.get("data").get("presentation").get("stayProductDetailPage").get("sections").get(sections/9/section/cardData/userId")
        return j

    def user_listing(self, user_id, limit=40, offset=10):
        user_id = base64.b64decode(user_id)
        user_id = "User:" + user_id.decode().split(":")[1]
        user_id = user_id.encode()
        user_id = base64.b64encode(user_id)
        user_id = user_id.decode()
        url =('https://www.airbnb.com/api/v3/GetUserProfile/operationName=GetUserProfile&locale=en&currency=USD&variables={"userId":"' +
              user_id + '","isPassportStampsEnabled":true,"mockIdentifier":null,"fetchCombinedSportsAndInterests":true}'
                        '&extensions={"persistedQuery":{"version":1,"sha256Hash":"a90837b2349a0f18d3263a34490277e72dccf91e3b9d2f96a9bcf65e4c68d43a"}}')
        url = 'https://www.airbnb.com/api/v3/GetUserProfile/?operationName=GetUserProfile&locale=en&currency=USD&variables={"userId":"' + user_id + '","isPassportStampsEnabled":true,"mockIdentifier":null,"fetchCombinedSportsAndInterests":true}&extensions={"persistedQuery":{"version":1,"sha256Hash":"a90837b2349a0f18d3263a34490277e72dccf91e3b9d2f96a9bcf65e4c68d43a"}}'
        headers = get_headers("headers_user_rooms.txt")  # ['user-agent'] = USER_AGENT[randint(0, len(USER_AGENT) - 1)]
        try:
            response = requests.get(url, headers=headers)
            j = response.json()
        except Exception as e:
            print(e)
            return
        # print(j)
        rooms_ids = [room.get("id") for room in j["data"]["presentation"]["userProfileContainer"]["userProfile"]["managedListings"]]

        print("user_rooms:", rooms_ids)

        # with open(f"user_listing-{user_id}.json", "w") as f:
        #     json.dump(j, f, ensure_ascii=False, indent=4)
        return rooms_ids

    # def user_info(self, user_id):
    #     url = 'https://www.airbnb.com/api/v3/GetConsentForUserQuery?operationName=GetConsentForUserQuery&locale=en&currency=USA&variables={"deviceId":"1676999524_MjE4MzJiMDA3MTQz","consentId":null,"includeConfigView":true}&extensions={"persistedQuery":{"version":1,"sha256Hash":"805bdcc4937dee31c2d53ae88f400d42c6637915a2cafc73f0b30a61c9ffda73"}}'
    #     print(j)
    #     with open("user_airbnb.json", "w") as f:
    #         json.dump(json.loads(j[0]), f, ensure_ascii=False, indent=4)

    def main(self, pages):
        items = []

        for page in range(1, pages + 1):
            print(f"page: {page}  ---------------------------------------------------")
            self.sleep()
            response = self.get_items(page)
            if response is None:
                print("Main response None")
                return
            j = response["data"]["presentation"]["explore"]["sections"][
                "sectionIndependentData"
            ]["staysSearch"]["searchResults"]
            print(f"Items on page {page}:", len(j))
            # items.append(j)

        # return
            for item in j:

                print("item:", item["listing"]["id"]) #
                items.append(self.get_room_info(item["listing"]["id"]))
                # if self.db.get_item(item["listing"]["id"]):
                #     print("Already exist main")
                #     continue
                self.sleep()
                userid = self.get_room_info(item["listing"]["id"])
                userid = userid["data"]["presentation"]["stayProductDetailPage"][
                    "sections"
                ]["sections"]
                # print(f"userid: {userid}")
                # continue
                # /data/presentation/stayProductDetailPage/sections/sections/9/section/cardData/userId
                for i in userid:
                    if i.get("section"):
                        if i.get("section").get("cardData"):
                            if i.get("section").get("cardData").get("userId"):
                                user_id = i["section"]["cardData"]["userId"]
                self.sleep()
                print("User ID:", user_id)
                # continue
                user_list = self.user_listing(user_id)

                print("user listing:", len(user_list))
                # continue
                # print(user_list)
                for l in user_list:
                    print(f"Item in user:{user_id} listing:", l)
                    # if self.db.get_item(l["id"]):
                    #     print("Already exist main")
                    #     continue
                    # self.sleep()
                    item_info = self.get_room_info(int(l))
                    items.append(item_info)
                with open(f"{self.region}.json", "w") as f:
                    json.dump(items, f, indent=4, ensure_ascii=False)



if __name__ == "__main__":
    # print(Airbnb().get_room_info(1150811899422579830))
    # with open(f"room_user_id.json", "w") as f:
    #     json.dump(Airbnb().room_user_id(20255447), f , indent=4)
    #
    Airbnb(region="Cuba").main(15)
    # Airbnb().user_listing("RGVtYW5kVXNlcjo0NTg0MjcxMg==") # 163663206
