from google.cloud import pubsub_v1
from service import Graphql,room_mapping,formating,formating2,sender
import json
import time

# TODO project           = "Your Google Cloud Project ID"
# TODO subscription_name = "Your Pubsub subscription name"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(
    'goquo-hotels-staging', 'room-mapping')

def callback(message):
    print('Received message: {}'.format(message))
    text = message._message.data
    json_response =json.loads(text.decode('utf8').replace("'", '"'))
    goquoHotelId = json_response['goquoHotelId']
    supplierCode = json_response['supplierCode']
    supplierHotelId = json_response['supplierHotelId']

    try:
        start = time.time()
        hotelid , room = Graphql(goquoHotelId, supplierCode, supplierHotelId)
        room_response=room_mapping(formating(hotelid, room),goquoHotelId)
        request_sender = formating2(room_response,goquoHotelId, supplierCode, supplierHotelId)
        sender(request_sender,goquoHotelId)
        end = time.time()
        print(" it is Processed in {}".format( end - start))
    except:
        print("connection has porblem !!!! ")
    time.sleep(10)
    message.ack()

future = subscriber.subscribe(subscription_path, callback=callback)
print (future.result())
# Blocks the thread while messages are coming in through the stream. Any
# exceptions that crop up on the thread will be set on the future.
try:
    # When timeout is unspecified, the result method waits indefinitely.
    future.result(timeout=60)
except Exception as e:
    print(
        'Listening for messages on {} threw an Exception: {}.'.format(
            'projects/goquo-hotels-staging/subscriptions/room-mapping', e))