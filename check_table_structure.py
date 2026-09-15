import pymysql


def check_table_structure():
    conn = pymysql.connect(
        host='localhost',
        port=3307,
        user='root',
        password='admin',
        database='prestashop',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute("DESCRIBE ps_customer")
            columns = cursor.fetchall()

            print("Структура таблицы ps_customer:")
            print("-" * 50)
            for col in columns:
                null = "NULL" if col['Null'] == 'YES' else "NOT NULL"
                default = f"Default: {col['Default']}" if col['Default'] is not None else "No default"
                print(f"{col['Field']:20} {col['Type']:15} {null:10} {default}")

            required_fields = []
            for col in columns:
                if col['Null'] == 'NO' and col['Default'] is None and col['Extra'] != 'auto_increment':
                    required_fields.append(col['Field'])

            if required_fields:
                print("\n Обязательные поля без значения по умолчанию:")
                for field in required_fields:
                    print(f"  - {field}")
            else:
                print("\nВсе обязательные поля имеют значения по умолчанию")

    finally:
        conn.close()


if __name__ == "__main__":
    check_table_structure()