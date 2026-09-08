from typing import Dict, Any, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TABLE_PREFIX = 'ps_'


def execute_query(connection, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            connection.commit()
            return result
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        connection.rollback()
        raise


def execute_query_all(connection, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise


def create_customer(connection, customer_data: dict) -> int:
    required_fields = ['firstname', 'lastname', 'email', 'passwd']
    for field in required_fields:
        if field not in customer_data:
            raise ValueError(f"Missing required field: {field}")

    query = f"""
        INSERT INTO {TABLE_PREFIX}customer 
        (id_shop, id_shop_group, id_gender, firstname, lastname, email, passwd, active, 
         date_add, date_upd, id_lang, id_default_group)
        VALUES 
        (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s)
    """

    params = (
        customer_data.get('id_shop', 1),
        customer_data.get('id_shop_group', 1),
        customer_data.get('id_gender', 1),
        customer_data['firstname'],
        customer_data['lastname'],
        customer_data['email'],
        customer_data['passwd'],
        customer_data.get('active', 1),
        customer_data.get('id_lang', 1),
        customer_data.get('id_default_group', 3)
    )

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        connection.commit()
        customer_id = cursor.lastrowid

        group_query = f"""
            INSERT INTO {TABLE_PREFIX}customer_group 
            (id_customer, id_group) 
            VALUES (%s, %s)
        """
        cursor.execute(group_query, (customer_id, customer_data.get('id_default_group', 3)))
        connection.commit()

        logger.info(f"Created customer with ID: {customer_id}")
        return customer_id


def get_customer_by_id(connection, customer_id: int) -> Optional[Dict[str, Any]]:
    query = f"""
        SELECT id_customer, id_gender, firstname, lastname, email, passwd, active, 
               date_add, date_upd, id_shop, id_lang, id_default_group
        FROM {TABLE_PREFIX}customer 
        WHERE id_customer = %s
    """

    return execute_query(connection, query, (customer_id,))


def update_customer(connection, customer_id: int, update_data: dict) -> bool:
    if not update_data:
        raise ValueError("Update data cannot be empty")

    existing = get_customer_by_id(connection, customer_id)
    if not existing:
        return False

    allowed_fields = ['firstname', 'lastname', 'email', 'passwd', 'active',
                      'id_lang', 'id_default_group', 'id_gender']

    set_clauses = []
    params = []

    for field, value in update_data.items():
        if field in allowed_fields:
            set_clauses.append(f"{field} = %s")
            params.append(value)

    if not set_clauses:
        raise ValueError("No valid fields to update")

    set_clauses.append("date_upd = NOW()")

    query = f"""
        UPDATE {TABLE_PREFIX}customer 
        SET {', '.join(set_clauses)}
        WHERE id_customer = %s
    """
    params.append(customer_id)

    with connection.cursor() as cursor:
        cursor.execute(query, tuple(params))
        connection.commit()
        logger.info(f"Updated customer with ID: {customer_id}")
        return True


def delete_customer(connection, customer_id: int) -> bool:
    existing = get_customer_by_id(connection, customer_id)
    if not existing:
        return False

    tables_to_clean = [
        f"{TABLE_PREFIX}customer_group",
        f"{TABLE_PREFIX}cart",
        f"{TABLE_PREFIX}order",
        f"{TABLE_PREFIX}address"
    ]

    with connection.cursor() as cursor:
        for table in tables_to_clean:
            try:
                cursor.execute(f"DELETE FROM {table} WHERE id_customer = %s", (customer_id,))
            except Exception as e:
                logger.warning(f"Could not delete from {table}: {e}")

        cursor.execute(f"DELETE FROM {TABLE_PREFIX}customer WHERE id_customer = %s", (customer_id,))
        connection.commit()
        logger.info(f"Deleted customer with ID: {customer_id}")
        return True


def get_customer_by_email(connection, email: str) -> Optional[Dict[str, Any]]:
    query = f"""
        SELECT id_customer, id_gender, firstname, lastname, email, passwd, active, 
               date_add, date_upd, id_shop, id_lang, id_default_group
        FROM {TABLE_PREFIX}customer 
        WHERE email = %s
    """

    return execute_query(connection, query, (email,))


def customer_exists(connection, customer_id: int) -> bool:
    result = get_customer_by_id(connection, customer_id)
    return result is not None