import json
import pika
import logging

from newsletter.models import Newsletter, UserContact

logging.basicConfig(level=logging.INFO)

credentials = pika.PlainCredentials("guest", "guest")
params = pika.ConnectionParameters(host="localhost", port=5672, credentials=credentials)
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue="sms_queue", durable=True)
logging.info("Waiting for sms for producer...")


def callback(ch, method, properties, body):
    """processing data received from producer,
    sending sms newsletter,
    saving newsletter status to database"""
    message = json.loads(body)

    logging.info(f"Received: {message.decode('utf-8')}")
    logging.info(f"Done {method.delivery_tag}")

    user_id = message.get("user_id")
    user_contact = UserContact.objects(user=user_id).first
    if not user_contact:
        logging.error(f"User contact not found for user id {user_id}")

    sms_send()

    newsletter = Newsletter(contact=user_contact.user, newsletter_status=True)
    newsletter.save()
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="sms_queue", on_message_callback=callback)

logging.info("Waiting for message...")
channel.start_consuming()


def sms_send():
    logging.info("SMS sended successfully")


sms_consumer = channel.start_consuming()
