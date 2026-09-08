import pytest
import pymysql
import os


def pytest_addoption(parser):
    parser.addoption("--host", action="store", default=os.getenv("DB_HOST", "localhost"), help="MySQL host")
    parser.addoption("--port", action="store", default=int(os.getenv("DB_PORT", 3307)), type=int, help="MySQL port")
    parser.addoption("--database", action="store", default=os.getenv("DB_NAME", "prestashop"), help="Database name")
    parser.addoption("--user", action="store", default=os.getenv("DB_USER", "root"), help="MySQL user")
    parser.addoption("--password", action="store", default=os.getenv("DB_PASSWORD", "admin"), help="MySQL password")


@pytest.fixture(scope="session")
def connection(request):
    host = request.config.getoption("--host")
    port = request.config.getoption("--port")
    database = request.config.getoption("--database")
    user = request.config.getoption("--user")
    password = request.config.getoption("--password")

    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10,
            autocommit=False
        )
        yield conn
        conn.close()
    except pymysql.err.OperationalError as e:
        pytest.fail(f"Не удалось подключиться к БД: {e}\n"
                    f"Проверьте:\n"
                    f"1. Запущен ли контейнер: docker ps\n"
                    f"2. Правильные ли параметры подключения (host={host}, port={port})\n"
                    f"3. Существует ли база данных '{database}'")