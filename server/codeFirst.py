import mysql.connector


def create_table_if_not_exists():
    conn = mysql.connector.connect(
        host="bz1fm6zwqfueyf94xgxi-mysql.services.clever-cloud.com",
        port=3306,
        user="uaxdsjzmqqypgfap",
        password="xD7LkYCtgvUfCv5yn3SE",
        database="bz1fm6zwqfueyf94xgxi"
    )
    cursor = conn.cursor()

    # בדיקה אם הטבלה קיימת
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = %s AND table_name = 'appointments'
    """, ('bz1fm6zwqfueyf94xgxi',))

    exists = cursor.fetchone()[0]

    if exists:
        print("ℹ️ הטבלה appointments כבר קיימת – לא נעשתה שום פעולה.")
    else:
        cursor.execute("""
            CREATE TABLE appointments (
                event_id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(20) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                email VARCHAR(255) NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                notes TEXT
            );
        """)
        print("✅ הטבלה appointments נוצרה בהצלחה.")

    cursor.close()
    conn.close()


# קריאה לפונקציה
create_table_if_not_exists()
# יצרת הטבלה בפעם הראשונה
# import mysql.connector
#
# conn = mysql.connector.connect(
#     host="bz1fm6zwqfueyf94xgxi-mysql.services.clever-cloud.com",
#     port=3306,
#     user="uaxdsjzmqqypgfap",
#     password="xD7LkYCtgvUfCv5yn3SE",
#     database="bz1fm6zwqfueyf94xgxi"
# )
#
# cursor = conn.cursor()
#
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS appointments (
#     event_id VARCHAR(255) PRIMARY KEY,
#     user_id VARCHAR(20) NOT NULL,
#     phone VARCHAR(20) NOT NULL,
#     email VARCHAR(255) NOT NULL,
#     start_time DATETIME NOT NULL,
#     end_time DATETIME NOT NULL,
#     notes TEXT
# );
# """)
#
# print("✅ טבלת appointments נוצרה בהצלחה.")
#
# cursor.close()
# conn.close()
