import json
import pymysql

def lambda_handler(event, context):
    print(event)

    rds_host  = "gifty-instance.c8dmkikrr98g.us-east-2.rds.amazonaws.com"
    name = "admin"
    password = "Matt1234"
    db_name = "Gifty"
    conn = pymysql.connect(rds_host, user=name, passwd=password, database=db_name, connect_timeout=5, autocommit=True)
    
    try:
        cursor = conn.cursor()

        print("here")
        #sqlCommand = "INSERT INTO Accounts(user,phone,bank,accessToken) VALUES ('%s','%s','%s','%s')" % \
        #             (body["username"], body["phone"], body["bankName"], accessToken)
        #print(sqlCommand)
        #cursor.execute(sqlCommand)
        print("SUCCESS")
    except Exception as e:
        print("ERROR")
    finally:
        conn.close()

    return {
        'statusCode': 200
    }