import json
import pymysql
import stripe

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
        # cursor.execute("Create TABLE Gifts(id INT NOT NULL AUTO_INCREMENT, toId varchar(20), fromId varchar(20), vendor varchar(50), paymentId varchar(50), caption varchar(280), amount decimal(5,2), remaining decimal(5,2), PRIMARY KEY (id)) ")
        # TODO: checks - user same as auth token, balance greater than gift amount, card belongs to user
        if body["paymentId"] == "Balance":
            # if balance: get balance from user, subtract amount from gift
            sqlCommand = "SELECT balance FROM Balance WHERE phone = '" + body["fromId"] + "'"
            print(sqlCommand)
            cursor.execute(sqlCommand)
            row = cursor.fetchone()
            prevBalance = float(row[0])
            newBalance = prevBalance - float(body["amount"])
            newBalancePrecison = format(newBalance, '.2f')
            sqlCommand = "Update Balance set balance = " + str(newBalancePrecison) + " WHERE phone = '" + body["fromId"] + "'"
            print(sqlCommand)
            cursor.execute(sqlCommand)
        else:
            # if card: get access token and stripe token, charge card
            # TODO: fix - generate new stripe token using plaid
            sqlCommand = "SELECT stripeToken FROM Accounts where accountId = '" + body["paymentId"] + "'"
            cursor.execute(sqlCommand)
            row = cursor.fetchone()
            stripeToken = row[0]
            print(stripeToken)
            
            stripe.api_key = "sk_test_8806eSVvnDhb9FvJjZKiEo4D00r8tYx1M9"
            charge = stripe.Charge.create(
                amount=body["amount"]*100, # Stripe takes the amount in cents
                currency="usd",
                source=stripeToken,
                description="Gifty charge for " + body["vendor"],
            )
            
            print(charge)
        
        sqlCommand = "INSERT INTO Gifts(toId,fromId,vendor,paymentId,caption,amount,remaining) VALUES ('%s','%s','%s','%s','%s',%.2f,%.2f)" % \
                     (body["toId"], body["fromId"], body["vendor"], body["paymentId"], body["caption"], body["amount"], body["amount"])
        print(sqlCommand)
        cursor.execute(sqlCommand)
        print("SUCCESS")
    except Exception as e:
        print("ERROR")
    finally:
        conn.close()

    return {
        'statusCode': 200
    }