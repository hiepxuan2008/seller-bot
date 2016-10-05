import os
import json

from logger import log
from flask import Flask, request
from messenger_api import *

app = Flask(__name__)

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                # https://developers.facebook.com/docs/messenger-platform/webhook-reference/message-received
                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message = messaging_event["message"]  # the message
                    on_message_received(sender_id, recipient_id, message)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                # https://developers.facebook.com/docs/messenger-platform/webhook-reference/postback-received
                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    payload = messaging_event["postback"]["payload"]  # the payload text
                    on_postback_received(sender_id, recipient_id, payload)
    
    return "ok", 200

params = {"access_token": os.environ["PAGE_ACCESS_TOKEN"]}
headers = {"Content-Type": "application/json"}
messenger = MessengerApi(params, headers)


def on_message_received(sender_id, recipient_id, message):
    messenger.do_sender_actions(sender_id)
    if not message.get("text"):
        return

    message_text = message["text"]
    if message_text == "help":
        help(sender_id)
    else:
        messenger.do_text_message(sender_id, "Invalid command, type help for the help")


def go_shopping(recipient_id):
    elements = [{
        "title": "Nice Blue T-Shirt - $19.99",
        "item_url": "http://www.lazada.vn/ao-thun-nam-co-tru-xanh-navi-2035572.html",
        "image_url": "http://vn-live-02.slatic.net/p/ao-thun-nam-co-tru-xanh-co-vit-1405-3755302-0a0daa09d238345d6a267ba403f7abbe-catalog_233.jpg",
        "buttons": [
            BuyButton().to_json()
        ]
    },
        {
            "title": "Light Green T-Shirt - $21.99",
            "item_url": "http://zanado.com/ao-thun-nam-jackies-b202-dep-gia-re-sid48907.html?color=98",
            "image_url": "http://a4vn.com/media/catalog/product/cache/all/thumbnail/255x298/7b8fef0172c2eb72dd8fd366c999954c/1/3/13_40_2.jpg",
            "buttons": [
                BuyButton().to_json()
            ]
        },
        {
            "title": "Raglan T-Shirt red & white- $12.99",
            "item_url": "http://www.lazada.vn/ao-thun-nam-tay-raglan-do-do-phoi-trang-2056856.html?mp=1",
            "image_url": "http://vn-live-01.slatic.net/p/ao-thun-nam-tay-raglan-do-do-phoi-trang-2581-6586502-2d977472b068b70467eeb4e9d2e1122d-catalog_233.jpg",
            "buttons": [
                BuyButton().to_json()
            ]
        }]

    messenger.do_generic_template(recipient_id, elements)


def shop_location(recipient_id):
    latitude = 10.762952
    longitude = 106.682340

    elements = [
        {
            'title': "Nova Shop",
            'subtitle': "227 Nguyen Van Cu, D5, HCM city",
            # 'image_url': 'http://staticmap.openstreetmap.de/staticmap.php?center=' + latitude + ',' + longitude + '&zoom=18&size=640x480&markers=' + latitude + ',' + longitude + ',ol-marker',
            'image_url': 'http://staticmap.openstreetmap.de/staticmap.php?center=10.762952,106.682340&zoom=15&size=640x480&markers=10.762952,106.682340,ol-marker',
            'buttons': [
                URLButton(
                    url='http://maps.google.com/maps?q=loc:10.762952,106.682340&z=20',
                    title="Show directions"
                ).to_json()
            ]
        }
    ]
    messenger.do_generic_template(recipient_id, elements)


def call_for_help(recipient_id):
    phone_number = "+84983892316"
    buttons = [
        CallButton(phone_number, phone_number).to_json()
    ]
    messenger.do_button_template(recipient_id, "Make a phone call", buttons)


def on_postback_received(sender_id, recipient_id, payload):
    if payload == "GO_SHOPPING":
        go_shopping(sender_id)
    elif payload == "SHOP_LOCATION":
        shop_location(sender_id)
    elif payload == "CALL_FOR_HELP":
        call_for_help(sender_id)

def help(recipient_id):
    text = "Hi, Can I help you?"
    buttons = [
        PostbackButton("Go Shopping", "GO_SHOPPING").to_json(),
        PostbackButton("Shop Location", "SHOP_LOCATION").to_json(),
        PostbackButton("Call For Help", "CALL_FOR_HELP").to_json()
    ]
    log(buttons)
    messenger.do_button_template(recipient_id, text, buttons)

if __name__ == '__main__':
    app.run(debug=True)