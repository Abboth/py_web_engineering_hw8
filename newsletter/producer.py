import pika
import logging

from data_processing import client
from newsletter.models import User, UserContact
from newsletter.consumer_sms import sms_consumer
from newsletter.consumer_email import email_consumer
from newsletter.seeds import insert_users

db = client["newsletter"]
collection = db["users"]

credentials = pika.PlainCredentials("guest", "guest")
params = pika.ConnectionParameters(host="localhost", port=5672, credentials=credentials)
connection = pika.BlockingConnection(params)
email_channel = connection.channel()

email_channel.queue_declare(queue="email_queue", durable=True)
email_channel.exchange_declare(exchange="email_newsletter", exchange_type="direct")
email_channel.queue_bind(exchange="email_newsletter", queue="email_queue")

sms_channel = connection.channel()
sms_channel.queue_declare(queue="sms_queue", durable=True)
sms_channel.exchange_declare(exchange="sms_newsletter", exchange_type="direct")
sms_channel.queue_bind(exchange="sms_newsletter", queue="sms_queue")

methods = {"phone": sms_channel, "email": email_channel}


def producer():
    """sending messages for every each subscriber from database
    with choosing of priority contact method"""
    users = User.objects()

    for user in users:
        contact = UserContact.objects(user=user).first()

        if not contact:
            logging.warning("Didn't find contact data for this user")
            continue

        for method in contact.contact_method_priority:
            if method in methods:
                contact_method = methods[method]
                message = {f"{method}": contact_method,
                           "user_id": str(user.id)}
                exchange = None
                routing_key = None
                match method:
                    case "phone":
                        exchange = "sms_newsletter"
                        routing_key = "sms_queue"
                    case "email":
                        exchange = "email_newsletter"
                        routing_key = "email_queue"

                contact_method.basic_publish(
                    exchange=exchange,
                    routing_key=routing_key,
                    body=str(message),
                    properties=pika.BasicProperties(
                        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                    ))
                logging.info(f"queue added for {contact_method}")

            else:
                logging.warning(f"contact doesn't want to get newsletters")

    connection.close()


if __name__ == "__main__":
    insert_users(15)
    producer()
    sms_consumer()
    email_consumer()
