import json
import pymysql
import stripe
import time

def lambda_handler(event, context):
    print(event)
    attributes = event["request"]["userAttributes"]
    userName = attributes["name"]
    # TODO: validate legal name

    rds_host  = "gifty-instance.c8dmkikrr98g.us-east-2.rds.amazonaws.com"
    name = "admin"
    password = "Matt1234"
    db_name = "Gifty"
    conn = pymysql.connect(rds_host, user=name, passwd=password, database=db_name, connect_timeout=5, autocommit=True)
    
    stripe.api_key = "sk_test_8806eSVvnDhb9FvJjZKiEo4D00r8tYx1M9"

    try:
        cursor = conn.cursor()
        
        cursor.execute("UPDATE Gifts SET toUser = '" + event["userName"] + "' WHERE toId = '" + attributes["phone_number"] + "';")

        resp = stripe.Account.create(
            type="custom",
            requested_capabilities=["transfers"],
            business_type="individual",
            business_profile= {"url": "molson194.github.io"}, # TODO: change website to gifty
            tos_acceptance={
                'date': int(time.time()),
                'ip': '8.8.8.8', # TODO: make them check a box on signup
            },
            individual={
                'first_name': userName.split()[0],
                'last_name': userName.split()[1]
            }
        )
        print(resp)
        
        sqlCommand = "INSERT INTO Balance(userId,phone,balance,stripeAccount) VALUES ('%s','%s',%.2f,'%s')" % \
                     (event["userName"], attributes["phone_number"], 0, resp["id"])
        print(sqlCommand)
        cursor.execute(sqlCommand)
        print("SUCCESS")
    except Exception as e:
        print("ERROR: " + str(e))
    finally:
        conn.close()
    return event