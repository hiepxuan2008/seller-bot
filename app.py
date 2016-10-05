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


def go_shopping(recipient_id):
    elements = [{
        "title": "Nice Blue T-Shirt - $19.99",
        "item_url": "http://www.lazada.vn/ao-thun-nam-co-tru-xanh-navi-2035572.html",
        "image_url": "http://vn-live-02.slatic.net/p/ao-thun-nam-co-tru-xanh-co-vit-1405-3755302-0a0daa09d238345d6a267ba403f7abbe-catalog_233.jpg",
        "buttons": [
            {
                "type": "web_url",
                "url": "http://www.lazada.vn/ao-thun-nam-co-tru-xanh-navi-2035572.html",
                "title": "Show now"
            },
            {
                "type": "postback",
                "title": "More feature",
                "payload": "FEATURE"
            }
        ]
    },
        {
            "title": "Light Green T-Shirt - $21.99",
            "item_url": "http://zanado.com/ao-thun-nam-jackies-b202-dep-gia-re-sid48907.html?color=98",
            "image_url": "http://a4vn.com/media/catalog/product/cache/all/thumbnail/255x298/7b8fef0172c2eb72dd8fd366c999954c/1/3/13_40_2.jpg",
            "buttons": [
                {
                    "type": "web_url",
                    "url": "http://zanado.com/ao-thun-nam-jackies-b202-dep-gia-re-sid48907.html?color=98",
                    "title": "Show now"
                }
            ]
        },
        {
            "title": "Raglan T-Shirt red & white- $12.99",
            "item_url": "http://www.lazada.vn/ao-thun-nam-tay-raglan-do-do-phoi-trang-2056856.html?mp=1",
            "image_url": "http://vn-live-01.slatic.net/p/ao-thun-nam-tay-raglan-do-do-phoi-trang-2581-6586502-2d977472b068b70467eeb4e9d2e1122d-catalog_233.jpg",
            "buttons": [
                {
                    "type": "web_url",
                    "url": "http://www.lazada.vn/ao-thun-nam-tay-raglan-do-do-phoi-trang-2056856.html?mp=1",
                    "title": "Show now"
                }
            ]
        }]

    messenger.do_generic_template(recipient_id, elements)
    pass


def on_postback_received(sender_id, recipient_id, payload):
    if payload == "GO_SHOPPING":
        go_shopping(sender_id)
    # showTShirtProducts(sender_id)
    # elif payload == "FEATURE":
    #      doMoreFeature(sender_id)
    # elif payload == "LOCATION":
    #     showLocation(sender_id)
    # elif payload == "VIDEO":
    #     showVideo(sender_id)


def showTShirtProducts(recipient_id):
    elements = [{
                    "title": "Nice Blue T-Shirt - $19.99",
                    "item_url": "http://www.lazada.vn/ao-thun-nam-co-tru-xanh-navi-2035572.html",
                    "image_url": "http://vn-live-02.slatic.net/p/ao-thun-nam-co-tru-xanh-co-vit-1405-3755302-0a0daa09d238345d6a267ba403f7abbe-catalog_233.jpg",
                    "buttons":[
                         {
                            "type":"web_url",
                            "url":"http://www.lazada.vn/ao-thun-nam-co-tru-xanh-navi-2035572.html",
                            "title":"Show now"
                         },
                         {
                             "type": "postback",
                             "title":"More feature",
                             "payload" : "FEATURE"
                         }
                    ]
                },
                {    
                    "title": "Light Green T-Shirt - $21.99",
                    "item_url": "http://zanado.com/ao-thun-nam-jackies-b202-dep-gia-re-sid48907.html?color=98",
                    "image_url": "http://a4vn.com/media/catalog/product/cache/all/thumbnail/255x298/7b8fef0172c2eb72dd8fd366c999954c/1/3/13_40_2.jpg",
                    "buttons":[
                         {
                            "type":"web_url",
                            "url":"http://zanado.com/ao-thun-nam-jackies-b202-dep-gia-re-sid48907.html?color=98",
                            "title":"Show now"
                         }
                    ]
                },
                {    
                    "title": "Raglan T-Shirt red & white- $12.99",
                    "item_url": "http://www.lazada.vn/ao-thun-nam-tay-raglan-do-do-phoi-trang-2056856.html?mp=1",
                    "image_url": "http://vn-live-01.slatic.net/p/ao-thun-nam-tay-raglan-do-do-phoi-trang-2581-6586502-2d977472b068b70467eeb4e9d2e1122d-catalog_233.jpg",
                    "buttons":[
                         {
                            "type":"web_url",
                            "url":"http://www.lazada.vn/ao-thun-nam-tay-raglan-do-do-phoi-trang-2056856.html?mp=1",
                            "title":"Show now"
                         }
                    ]
                }]

    messenger.do_generic_template(recipient_id, elements)

def doMoreFeature(recipient_id):
    data = json.dumps({
    "recipient":{
        "id":recipient_id
      },
      "message":{
        "attachment":{
          "type":"template",
          "payload":{
            "template_type":"button",
            "text":"What do you want to do next?",
            "buttons":[
              {
                "type":"postback",
                "title":"Products on Video",
                "payload": "VIDEO"
              },
              {
                "type":"postback",
                "title":"Shop location",
                "payload":"LOCATION"
              },
              {
                "type":"postback",
                "title":"Show webiste",
                "payload":"WEBSITE"
              }
            ]
          }
        }
      }
    })
    messenger.postData(data)


def help(recipient_id):
    text = "Hi, Can I help you?"
    buttons = [
        PostbackButton("Go Shopping", "GO_SHOPPING").to_json(),
        PostbackButton("Shop Location", "SHOP_LOCATION").to_json(),
        PostbackButton("Call For Help", "CALL_FOR_HELP").to_json()
    ]
    log(buttons)
    messenger.do_button_template(recipient_id, text, buttons)


def greeting(recipient_id):
    text = "Welcome to Nova shop, what are you looking for today?"
    buttons = [
                  {
                    "type":"postback",
                    "title":"T-Shirt",
                    "payload":"T_SHIRT"
                  },
                  {
                    "type":"postback",
                    "title":"Jean",
                    "payload":"JEAN"
                  },
                  {
                    "type":"postback",
                    "title":"Wallet",
                    "payload":"WALLET"
                  }
            ]
    messenger.do_button_template(recipient_id, text, buttons)


if __name__ == '__main__':
    app.run(debug=True)