import json
import pymysql
import stripe
import time

def lambda_handler(event, context):
    print(event)
    print(event["body"])
    body = json.loads(event["body"])
    rds_host  = "gifty-instance.c8dmkikrr98g.us-east-2.rds.amazonaws.com"
    name = "admin"
    password = "Matt1234"
    db_name = "Gifty"
    conn = pymysql.connect(rds_host, user=name, passwd=password, database=db_name, connect_timeout=5, autocommit=True)
    try:
        cursor = conn.cursor()
        sqlCommand = "SELECT balance FROM Balance WHERE userId = '" + body["user"] + "'"
        print(sqlCommand)
        cursor.execute(sqlCommand)
        row = cursor.fetchone()

        # TODO: never go below balance
        balance = float(row[0])
        newBalance = balance - body["amountCashout"]
        newBalance = format(newBalance, '.2f')
            
        # TODO: get user id
        sqlCommand = "SELECT stripeToken FROM Accounts where accountId = '" + body["paymentId"] + "'"
        cursor.execute(sqlCommand)
        row = cursor.fetchone()
        stripeToken = row[0]
        print(stripeToken)
        stripe.api_key = "sk_test_8806eSVvnDhb9FvJjZKiEo4D00r8tYx1M9"
        
        # HACK HACK HACK: create a connected account on the fly and charge that account
        stripe.Account.modify(
            "acct_1Fu3heFtQv05NP3X",
            tos_acceptance={
                'date': int(time.time()),
                'ip': '8.8.8.8', # Depends on what web framework you're using
            }
        )
        #stripeResponse = stripe.Transfer.create(
        #    amount=body["amountCashout"] * 100, 
        #    currency="usd",
        #    destination= "acct_1Fu3heFtQv05NP3X"
        #)
        
        print(stripeResponse)

        # TODO: Only update balance if stripe response successful
        sqlCommand = "Update Balance set balance = " + str(newBalance) + " WHERE userId = '" + body["user"] + "'"
        print(sqlCommand)
        #cursor.execute(sqlCommand)
        
        print("SUCCESS")
    except Exception as e:
        print("ERROR: " + str(e))
    finally:
        conn.close()

    return {
        'statusCode': 200
    }