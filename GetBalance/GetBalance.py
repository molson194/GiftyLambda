import json
import pymysql

def lambda_handler(event, context):
    print(event)
    body = json.loads(event["body"])
    rds_host  = "gifty-instance.c8dmkikrr98g.us-east-2.rds.amazonaws.com"
    name = "admin"
    password = "Matt1234"
    db_name = "Gifty"
    conn = pymysql.connect(rds_host, user=name, passwd=password, database=db_name, connect_timeout=5, autocommit=True)
    
    try:
        cursor = conn.cursor()

        balance = 0
        sqlCommand = "SELECT balance FROM Balance WHERE userId = '" + body["userId"] + "'"
        print(sqlCommand)
        cursor.execute(sqlCommand)
        row = cursor.fetchone()
        print(row)
        balance = row[0]
        print("SUCCESS")
    except Exception as e:
        print("ERROR: " + str(e))
    finally:
        conn.close()

    return {
        'statusCode': 200,
        'body': balance
    }