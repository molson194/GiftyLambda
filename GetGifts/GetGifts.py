import json
import pymysql

def lambda_handler(event, context):
    print(event)
    body = json.loads(event["body"])
    rds_host  = "gifty-instance.c8dmkikrr98g.us-east-2.rds.amazonaws.com"
    name = "admin"
    password = "Matt1234"
    db_name = "Gifty"
    conn = pymysql.connect(rds_host, user=name, passwd=password, database=db_name, connect_timeout=5)
    try:
        cursor = conn.cursor()
        #cursor.execute("SHOW columns FROM Gifts")
        #print([column[0] for column in cursor.fetchall()])
        sqlCommand = "SELECT id,vendor,caption,remaining,fromId FROM Gifts WHERE toID = '" + body["phoneNumber"] + "'"
        print(sqlCommand)
        cursor.execute(sqlCommand)
        rows = cursor.fetchall()
        
        gifts = []
        for row in rows:
            print(row)
            gift = {"id": row[0], "vendor": row[1], "caption": row[2], "remainingBalance": str(row[3]), "fromId": row[4]}
            gifts.append(gift)
        print(gifts)
        print("SUCCESS")
    except Exception as e:
        print(e)
    finally:
        conn.close()

    return {
        'statusCode': 200,
        'body': json.dumps(gifts)
    }