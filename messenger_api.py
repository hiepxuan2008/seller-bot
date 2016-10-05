import json
import requests
import logger


class MessengerApi:
    def __init__(self, params, headers):
        self.params = params
        self.headers = headers

    def post_data(self, data):
        r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=self.params, headers=self.headers, data=data)
        if r.status_code != 200:
            logger.log(r.status_code)
            logger.log(r.text)

    # Sender Actions
    # https://developers.facebook.com/docs/messenger-platform/send-api-reference/sender-actions
    def do_sender_actions(self, recipient_id):
        data = json.dumps({
          "recipient":{
              "id":recipient_id
          },
          "sender_action":"typing_on"
        })
        self.post_data(data)

    # Text Message
    # https://developers.facebook.com/docs/messenger-platform/send-api-reference/text-message
    def do_text_message(self, recipient_id, message_text):
        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message_text
            }
        })
        self.post_data(data)

    # Image Attachment
    # https://developers.facebook.com/docs/messenger-platform/send-api-reference/image-attachment
    def do_image_attachment(self, recipient_id, image_url):
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
        self.post_data(data)

    # Audio Attachment
    # https://developers.facebook.com/docs/messenger-platform/send-api-reference/audio-attachment
    def do_audio_attachment(self, recipient_id, audio_url):
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
        self.post_data(data)

    # Video Attachment
    # https://developers.facebook.com/docs/messenger-platform/send-api-reference/video-attachment
    def do_video_attachment(self, recipient_id, video_url):
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
        self.post_data(data)

    # File Attachment
    # https://developers.facebook.com/docs/messenger-platform/send-api-reference/file-attachment
    def do_file_attachment(self, recipient_id, file_url):
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
        self.post_data(data)

    # Generic Template
    # https://developers.facebook.com/docs/messenger-platform/send-api-reference/generic-template
    def do_generic_template(self, recipient_id, elements):
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

        self.post_data(data)

    # Button Template
    # https://developers.facebook.com/docs/messenger-platform/send-api-reference/button-template
    # Params:
    #    text: must be UTF-8 and has a 320 character limit
    #    buttons: is limited to 3

    def do_button_template(self, recipient_id, text, buttons):
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

        self.post_data(data)

    # Receipt Template
    # https://developers.facebook.com/docs/messenger-platform/send-api-reference/receipt-template

    def do_receipt_template(self, recipient_id, recipient_name, order_number, currency, payment_method, order_url, timestamp, elements, address, summary, adjustments):
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

        self.post_data(data)


class PostbackButton:
    def __init__(self, title, postback_value):
        self.title = title
        self.postback_value = postback_value

    def to_json(self):
        return json.dumps({
            "type":"postback",
            "title":self.title,
            "payload":self.postback_value
        })

class CallButton:
    def __init__(self, title, phone_number):
        self.title = title
        self.phone_number = phone_number

    def to_json(self):
        return json.dumps({
            "type":"phone_number",
            "title":self.title,
            "payload":self.phone_number
        })