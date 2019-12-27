import json
import pymysql

def lambda_handler(event, context):
    rds_host  = "gifty-db-instance-1.c8dmkikrr98g.us-east-2.rds.amazonaws.com"
    name = "admin"
    password = "Matt1234"
    db_name = "Gifty"
    conn = pymysql.connect(rds_host, user=name, passwd=password, database=db_name, connect_timeout=5)
    try:
        cursor = conn.cursor()
        sqlCommand = "SELECT * FROM Gifts WHERE toID = '+13035147424'"
        cursor.execute(sqlCommand)
        rows = cursor.fetchall()
        
        gifts = []
        for row in rows:
            print(row)
            gift = {"vendor": row[2], "toId": row[0], "remainingBalance": str(row[6]), "fromId": row[1]}
            gifts.append(gift)
        print(gifts)
        print("SUCCESS")
    except Exception as e:
        print("ERROR")
    finally:
        conn.close()

    return {
        'statusCode': 200,
        'body': json.dumps(gifts)
    }