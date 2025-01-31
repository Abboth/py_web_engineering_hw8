import logging
import random

import faker
from newsletter.models import Newsletter, UserContact, User
from pymongo import errors

logging.basicConfig(level=logging.INFO)
fake = faker.Faker()

contact_method = ["phone", "email"]


def insert_users(count_of_subscribers):
    """Inserting fake users to mongodb"""
    try:
        for _ in range(count_of_subscribers):
            user = User(name=fake.name,
                        age=fake.age)
            user.save()

            contact = UserContact(user=user,
                                  phone=fake.phone,
                                  email=fake.email,
                                  contact_method_priority=random.choice(contact_method))
            contact.save()

            newsletter = Newsletter(contact=contact)
            newsletter.save()
        logging.info('Added users to mongodb')
    except errors.PyMongoError as err:
        logging.error(f"Failed to seed data by users: {err}")
