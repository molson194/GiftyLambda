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

        # cursor.execute("Create TABLE DeviceTokens(user varchar(50), token varchar(100)) ")
        # if user already exists replace token
        cursor.execute("SELECT * FROM DeviceTokens WHERE user = '%s'" % (body["user"]))
        row_count = cursor.rowcount
        if row_count == 0:
            sqlCommand = "INSERT INTO DeviceTokens(user,token) VALUES ('%s','%s')" % (body["user"], body["token"])
        else:
            sqlCommand = "UPDATE DeviceTokens set token = '" + body["token"] + "' where user = '" + body["user"] + "'"
        print(sqlCommand)
        cursor.execute(sqlCommand)
        print("SUCCESS")
    except Exception as e:
        print("ERROR: " + str(e))
    finally:
        conn.close()

    return {
        'statusCode': 200
    }