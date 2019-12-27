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
        sqlCommand = "SELECT bank,accountId,accountMask,accountName,accountType,accountSubtype FROM Accounts WHERE user = '" + body["user"] + "'"
        print(sqlCommand)
        cursor.execute(sqlCommand)
        rows = cursor.fetchall()
        accounts = []
        for row in rows:
            account = {"bank": row[0], "accountId": row[1], "accountMask": row[2], "accountName": row[3], "accountType": row[4], "accountSubtype":row[5]}
            accounts.append(account)
        print(accounts)
        print("SUCCESS")
    except Exception as e:
        print("ERROR: " + str(e))
    finally:
        conn.close()

    return {
        'statusCode': 200,
        'body': json.dumps(accounts)
    }