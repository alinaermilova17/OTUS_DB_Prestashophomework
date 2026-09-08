import pymysql
import sys


def check_connection():
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='admin',
            database='prestashop',
            connect_timeout=5
        )
        print(" Подключение к MySQL в Docker успешно!")

        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f" Тестовый запрос выполнен: {result}")

            cursor.execute("SHOW TABLES LIKE 'ps_customer'")
            tables = cursor.fetchall()
            if tables:
                print(" Таблица ps_customer существует")
            else:
                print("Таблица ps_customer не найдена. Убедитесь, что PrestaShop установлен")

        conn.close()
        return True
    except Exception as e:
        print(f" Ошибка подключения: {e}")
        print("\nПроверьте:")
        print("1. Запущен ли контейнер: docker ps | grep prestashop_mysql")
        print("2. Правильный ли порт: 3307")
        print("3. Правильный ли пароль: admin")
        return False


if __name__ == "__main__":
    sys.exit(0 if check_connection() else 1)