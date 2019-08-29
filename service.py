#import library
import requests
import json
import re
import inflect
p = inflect.engine()
with open(r'dictionry\accommodateTypes.json') as json_file:
    acccomodate_dic = json.load(json_file)
with open(r'dictionry\roomTypeWithValue.json') as json_file:
    roomType_dic = json.load(json_file)
with open(r'dictionry\bedlogic.json') as json_file:
    bedlogic_dic = json.load(json_file)
#Extract Data from GraphQL
def Graphql (hotelid,supplierCode,supplierHotelId):

    try:
        url = "http://192.168.0.70:3001/graphql"
        # url = "http://contentstore.explura.co/graphql"
        payload = "{\"query\":\"{ roomTypes(goquoHotelId: \\\"" +  hotelid + "\\\", supplierCode: \\\""+ supplierCode +"\\\", supplierHotelId: \\\""+ supplierHotelId +"\\\", roomTypeCodes:[], page:1, pageSize:999999) { count, roomTypes{ goquoHotelId, supplierCode, supplierHotelId, roomTypeCode, roomTypeName, description, spaceType{ code, name, }, roomCharacteristic{ code, name, }, maxOccupancy, numberOfRoom, numberOfBedroomsPerRoom, isSharedAccommodation, sizeSqm, view, noWindows, hasConnectingRooms, roomTypeAmenities{ amenityCode, amenityName, amenityGroupCode, amenityGroupName, amenityAttributes{ amenityAttributeCode, amenityAttributeName, dataType, attributeValue, } } bedTypeConfigurations{ bedTypeCombination{ bedType, quantity, } } } } }\"}"

        # payload = "{\n\t\"query\":\"{RoomTypes(goquoHotelId:\\\"" + hotelid + "\\\",supplierCode:\\\"" + supplierCode + "\\\",supplierHotelId:\\\"" + supplierHotelId +"\\\",roomTypeAmenityKeys:[\\\"bed\\\"]){goquoHotelId,supplierCode,supplierHotelId,roomTypeCode,roomTypeName,description,maxOccupancy,size{squareFeet,squareMetres,},view,isSharedAccommodation,hasConnectingRooms}}\"\n}"
        # payload = "{\r\n\t\"query\":\"{roomTypes(goquoHotelId: \\\"" +  hotelid + "\\\", supplierCode: \\\""+ supplierCode +"\\\", supplierHotelId: \\\""+ supplierHotelId +"\\\", roomTypeAmenityKeys: []) {goquoHotelId,supplierCode,supplierHotelId,roomTypeCode,roomTypeName,description,spaceType{code,name,},roomCharacteristic{code,name,}maxOccupancy,size{squareFeet,squareMetres},view,noWindows,hasConnectingRooms,directAccess{swimmingPool,privateBeach}}}\"\r\n}"

        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            'Postman-Token': "5dc1a607-f2aa-460c-b361-e8d021484738"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        response_json = json.loads(response.text)

        room = []

        for key,value in enumerate( response_json['data']['roomTypes']['roomTypes']):
            value['name'] = value.pop('roomTypeName')
            value['id'] = key
            room.append(value)
        Hotelid = response_json['data']['roomTypes']['roomTypes'][0]['goquoHotelId']
        return Hotelid,room

    except Exception as ex:
        print('GraphQL process has problem in : ' + str(ex) + +' in ' + str(hotelid) + str(supplierCode) + str(supplierHotelId))
        return {}

#Create formating for base on room mapping API
def formating(Hotelid ,room):

    request_roommapping = {"Hotels" : [ {
        "hotelId": Hotelid,
        "availableRooms": [
            {
                "availableRoomTypes": room
            }
        ]
    }
    ]
    }

    json_request = json.dumps(request_roommapping)
    return json_request

#Room Mapping API
def room_mapping (request_json,Hotelid):
    url = "https://goquopro.appspot.com/api/v1/room-mapping"

    payload = str(request_json)
    headers = {
        'Content-Type': "application/json",
        'cache-control': "no-cache",
        'Postman-Token': "96bec713-5ad9-48c0-8fa0-445f3157f22b"
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    response_json = json.loads(response.text)
    for value in response_json['Hotels'][0]['availableRooms'][0]['availableRoomTypes']:
        value = improve(value)
        del value['AIDetails']

    # print("Goquo Hotel ID {} is mapped".format(Hotelid) if response.text else ' Goquo Hotel ID {} not mapped'.format(Hotelid))
    return response_json

def formating2(response,goquoid,suppliercode,supplierhotelid):

    for value in response['Hotels'][0]['availableRooms'][0]['availableRoomTypes']:
            value['roomTypeName'] = value.pop('name')


    request_sender = {"goquoHotelId":goquoid ,
                      "supplierCode":suppliercode ,
                      "supplierHotelId":supplierhotelid,
                      "roomMapping":response
    }

    json_request = json.dumps(request_sender)
    return json_request

def sender (request_sender,goquoid):

        url = "http://contentstore.explura.co/api/roomMappings"

        payload = str(request_sender)
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            'Postman-Token': "f1babf2e-4543-4eab-a069-7e1f27a64cef"
            }

        response = requests.request("PUT", url, data=payload, headers=headers)
        print ("hotel {} is sent".format(goquoid))
        print(response.text)
def room_character (room):
    rmp = []
    for acc in roomType_dic:
        if acc['name'][0] in room:
            rmp.append(acc)
    if rmp == []:
        room_name = 'run of the house'
    else :
        def myFunc(e):
            return e['value']

        rmp.sort(key=myFunc)
        temp = []
        for i in rmp:
            if i['title'] not in temp:
                temp.append(i['title'])
        room_name = ' '.join(temp)


    return room_name

def bedImrove (beds):
    bed_list = []
    max_ocp= []
    for bed in beds:
        temp = []
        temp_ocp = 0
        for data in bed['bedTypeCombination']:
            for i in  bedlogic_dic:
               if  i['bed'] in data['bedType'].lower():
                   temp_ocp += data['quantity'] * i['person']
                   numebr = p.number_to_words(data['quantity'])
                   if i['bed'] == "femalecapsule":
                       i['bed'] = "female capsule"
                   if i['bed'] == "malecapsule":
                       i['bed'] = "male capsule"
                   temp.append(numebr.capitalize() + " "  + i['bed'].capitalize())
                   break

        max_ocp.append(temp_ocp)
        bed_list.append(' and '.join(temp))
    # for bed in beds:
    #     temp = []
    #     temp_ocp = 0
    #     for data in bed['bedTypeCombination']:
    #         numebr = p.number_to_words(data['quantity'])
    #         temp.append (numebr.capitalize()  +" " +data['bedType'].capitalize() )
    #         for i in  bedlogic_dic:
    #            if data['bedType'] == i['bed'] in data['bedType']:
    #                temp_ocp += data['quantity'] * i['person']
    #     max_ocp.append(temp_ocp)
    #     bed_list.append(' '.join(temp))
    max_occupancy = max (max_ocp)
    return bed_list, max_occupancy
# a = room_character('f23 deluxe club 21 suite double bed')

 # or view_room != 0 or view_room != 'no' or view_room != 'no windows view' or view_room != 'no Windows' or view_room != 'no view'
def improve (room):
    #Improve View
    if room['viewLabel'][0] == 'not specified' and room['view'] :
            view_room = ' '.join(re.findall('[a-zA-Z]+', str(room['view'][0]))).lower()

            if re.findall('view', view_room):
                    room['viewLabel'][0] = view_room
                    # print('view features is changes to ' + view_room )

            else :
                    room['viewLabel'][0] = view_room + ' view'
                    # print('view features is changes to ' + view_room)

    # else :
    #     room['viewLabel'][0] = 'not specified'

    #Imporve Bed Type
    # if room['bedTypeLabel'][0] == 'Double/Twin' and room['bedTypeConfigurations']:
    maxocp = 2
    if room['bedTypeConfigurations']:
       beds , maxocp = bedImrove(room['bedTypeConfigurations'])
       room['bedTypeLabel'] = beds

    else :
        max_ocp = []
        for bed in room['bedTypeLabel']:
            for i in bedlogic_dic:
                if bed.lower() == i['bed']:
                    max_ocp.append( i['person'])
        maxocp = max(max_ocp)



    # #improve max_occupacey
    #     # if room['maxOccupancy'] and room['maxOccupancy'] < 50 :
    #     #     room['maxOccupancy']
    #     # else :
    #     #     room['maxOccupancy'] = maxocp

    #Improve Room Type
    if room['roomTypeLabel'][0] == 'run of the house' and room['roomCharacteristic']:
        room_ch = str (room['roomCharacteristic']['name'])
        room['roomTypeLabel'][0] = room_character(room_ch.lower())



    return room
# hotelid, room =Graphql('148828','AGD','147902')
# room_response = room_mapping(formating(hotelid, room),'148828')
# # room_response = room_mapping(formating(hotelid, room), '2699954')
# # request_sender = formating2(room_response, '2699954','AGD','1198445')
# # sender(request_sender, '2699954')
print('done')