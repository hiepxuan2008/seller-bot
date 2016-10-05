import os
import sys
import json

import requests
from flask import Flask, request

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

				if messaging_event.get("message"):  # someone sent us a message
					sender_id = messaging_event["sender"]["id"]		# the facebook ID of the person sending you the message
					recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
					message_text = messaging_event["message"]["text"]  # the message's text

					onMessageEvent(sender_id, recipient_id, message_text)

				if messaging_event.get("delivery"):  # delivery confirmation
					pass

				if messaging_event.get("optin"):  # optin confirmation
					pass

				if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
					sender_id = messaging_event["sender"]["id"]		# the facebook ID of the person sending you the message
					recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
					payload = messaging_event["postback"]["payload"]  # the payload text
					onPostbackEvent(sender_id, recipient_id, payload)

	return "ok", 200

def postData(data):
	params = {
		"access_token": os.environ["PAGE_ACCESS_TOKEN"]
	}
	headers = {
		"Content-Type": "application/json"
	}

	r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
	if r.status_code != 200:
		log(r.status_code)
		log(r.text)

def onPostbackEvent(sender_id, recipient_id, payload):
	if payload == "T_SHIRT":
		showTShirtProducts(sender_id)
	# elif payload == "FEATURE":
	# 	doMoreFeature(sender_id)
	# elif payload == "LOCATION":
	# 	showLocation(sender_id)
	# elif payload == "VIDEO":
	# 	showVideo(sender_id)

def showTShirtProducts(recipient_id):
	elements = [{
					"title": "Welcome to Peter\'s Hats",
					"item_url": "https://petersfancybrownhats.com",
					"image_url": "https://petersfancybrownhats.com/company_image.png",
					"subtitle": "We\'ve got the right hat for everyone.",
					"buttons": [{
						"type": "web_url",
						"url": "https://petersfancybrownhats.com",
						"title": "View Website"
					}, {
						"type": "postback",
						"title": "Start Chatting",
						"payload": "DEVELOPER_DEFINED_PAYLOAD"
					}]
				}]
				
	doGenericTemplate(recipient_id, elements)

def onMessageEvent(sender_id, recipient_id, message_text):
	doSenderActions(sender_id)
	if message_text == "hello":
		greeting(sender_id)

def greeting(sender_id):
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
	doButtonTemplate(sender_id, text, buttons)



# -------------------------- FB Messenger API Functions -----------------
# Sender Actions
# https://developers.facebook.com/docs/messenger-platform/send-api-reference/sender-actions
def doSenderActions(recipient_id):
	data = json.dumps({
	  "recipient":{
	  	"id":recipient_id
	  },
	  "sender_action":"typing_on"
	})
	postData(data)

# Text Message
# https://developers.facebook.com/docs/messenger-platform/send-api-reference/text-message
def doTextMessage(recipient_id, message_text):
	data = json.dumps({
		"recipient": {
			"id": recipient_id
		},
		"message": {
			"text": message_text
		}
	})
	postData(data)

# Image Attachment
# https://developers.facebook.com/docs/messenger-platform/send-api-reference/image-attachment
def doImageAttachment(recipient_id, image_url):
	data = json.dumps({
			"recipient":{
				"id":recipient_id
			},
			"message":{
				"attachment":{
				"type":"image",
				"payload":{
					"url":image_url
				}
			}
		}
	})
	postData(data)

# Audio Attachment
# https://developers.facebook.com/docs/messenger-platform/send-api-reference/audio-attachment
def doAudioAttachment(recipient_id, audio_url):
	data = json.dumps({
			"recipient":{
				"id":recipient_id
			},
			"message":{
				"attachment":{
				"type":"audio",
				"payload":{
					"url":audio_url
				}
			}
		}
	})
	postData(data)

# Video Attachment
# https://developers.facebook.com/docs/messenger-platform/send-api-reference/video-attachment
def doVideoAttachment(recipient_id, video_url):
	data = json.dumps({
			"recipient":{
				"id":recipient_id
			},
			"message":{
				"attachment":{
				"type":"video",
				"payload":{
					"url":video_url
				}
			}
		}
	})
	postData(data)

# File Attachment
# https://developers.facebook.com/docs/messenger-platform/send-api-reference/file-attachment
def doFileAttachment(recipient_id, file_url):
	data = json.dumps({
			"recipient":{
				"id":recipient_id
			},
			"message":{
				"attachment":{
				"type":"file",
				"payload":{
					"url":file_url
				}
			}
		}
	})
	postData(data)

# Generic Template
# https://developers.facebook.com/docs/messenger-platform/send-api-reference/generic-template
def doGenericTemplate(recipient_id, elements):
	data = json.dumps({
		"recipient":{
			"id":recipient_id
		},
		"message":{
			"attachment":{
			"type":"template",
			"payload":{
				"template_type":"generic",
				"elements":elements
				}
			}
		}
	})

	postData(data)

# Button Template
# https://developers.facebook.com/docs/messenger-platform/send-api-reference/button-template
# Params: 
#	text: must be UTF-8 and has a 320 character limit
#	buttons: is limited to 3

def doButtonTemplate(recipient_id, text, buttons):
	data = json.dumps({
		  "recipient":{
			"id":recipient_id
		  },
		  "message":{
			"attachment":{
			  "type":"template",
			  "payload":{
				"template_type":"button",
				"text":text,
				"buttons": buttons
			  }
			}
		  }
		})

	postData(data)

# Receipt Template
# https://developers.facebook.com/docs/messenger-platform/send-api-reference/receipt-template

def doReceiptTemplate(recipient_id, recipient_name, order_number, currency, payment_method, order_url, timestamp, elements, address, summary, adjustments):
	data = json.dumps({
	"recipient":{
		"id":recipient_id
	},
	"message":{
		"attachment":{
			"type":"template",
			"payload":{
				"template_type":"receipt",
				"recipient_name":recipient_name,
				"order_number":order_number,
				"currency":currency,
				"payment_method":payment_method,		
				"order_url":order_url,
				"timestamp":timestamp, 
				"elements":elements,
				"address":address,
				"summary":summary,
				"adjustments":adjustments
				}
			}
		}
	})

	postData(data)

 # simple wrapper for logging to stdout on heroku
def log(message): 
	print str(message)
	sys.stdout.flush()


if __name__ == '__main__':
	app.run(debug=True)