import random
import string
from lib.db import create_customer, get_customer_by_id, update_customer, delete_customer, customer_exists


def generate_random_email():
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"test_{random_string}@example.com"


def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))


class TestCustomer:

    def test_create_customer(self, connection):
        customer_data = {
            'firstname': generate_random_string(),
            'lastname': generate_random_string(),
            'email': generate_random_email(),
            'passwd': 'password123',
            'active': 1,
            'id_gender': 1
        }

        customer_id = create_customer(connection, customer_data)
        assert customer_id > 0

        created_customer = get_customer_by_id(connection, customer_id)
        assert created_customer is not None
        assert created_customer['firstname'] == customer_data['firstname']
        assert created_customer['lastname'] == customer_data['lastname']
        assert created_customer['email'] == customer_data['email']
        assert created_customer['id_gender'] == customer_data['id_gender']

        delete_customer(connection, customer_id)

    def test_update_customer(self, connection):
        customer_data = {
            'firstname': generate_random_string(),
            'lastname': generate_random_string(),
            'email': generate_random_email(),
            'passwd': 'password123',
            'id_gender': 1
        }
        customer_id = create_customer(connection, customer_data)

        new_firstname = generate_random_string()
        new_lastname = generate_random_string()
        new_email = generate_random_email()

        update_data = {
            'firstname': new_firstname,
            'lastname': new_lastname,
            'email': new_email,
            'id_gender': 2
        }

        result = update_customer(connection, customer_id, update_data)
        assert result is True

        updated_customer = get_customer_by_id(connection, customer_id)
        assert updated_customer is not None
        assert updated_customer['firstname'] == new_firstname
        assert updated_customer['lastname'] == new_lastname
        assert updated_customer['email'] == new_email
        assert updated_customer['id_gender'] == 2

        delete_customer(connection, customer_id)

    def test_update_non_existent_customer(self, connection):
        non_existent_id = 9999999

        update_data = {
            'firstname': 'NewName',
            'lastname': 'NewLastName',
            'email': 'newemail@example.com'
        }

        result = update_customer(connection, non_existent_id, update_data)
        assert result is False

    def test_delete_customer(self, connection):
        customer_data = {
            'firstname': generate_random_string(),
            'lastname': generate_random_string(),
            'email': generate_random_email(),
            'passwd': 'password123',
            'id_gender': 1
        }
        customer_id = create_customer(connection, customer_data)

        assert customer_exists(connection, customer_id) is True

        result = delete_customer(connection, customer_id)
        assert result is True

        deleted_customer = get_customer_by_id(connection, customer_id)
        assert deleted_customer is None

    def test_delete_non_existent_customer(self, connection):
        non_existent_id = 9999999

        result = delete_customer(connection, non_existent_id)
        assert result is False