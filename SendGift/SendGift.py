import json
import pymysql
import stripe
import plaid
import boto3

def lambda_handler(event, context):
    print(event)
    print(event["body"])
    body = json.loads(event["body"])
    
    rds_host  = "gifty-instance.c8dmkikrr98g.us-east-2.rds.amazonaws.com"
    name = "admin"
    password = "Matt1234"
    db_name = "Gifty"
    conn = pymysql.connect(rds_host, user=name, passwd=password, database=db_name, connect_timeout=5, autocommit=True)
    
    PLAID_CLIENT_ID="5da75fda7e517c0013053c50"
    PLAID_SECRET="d5e85fc65bace5c0b03e3db352bc78"
    PLAID_PUBLIC_KEY="72a81b8e9f3672dbfd85efc24eb0f8"
    PLAID_ENV="sandbox"
    client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET, public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, api_version='2019-05-29')

    stripe.api_key = "sk_test_8806eSVvnDhb9FvJjZKiEo4D00r8tYx1M9"
    
    client = boto3.client(
        'pinpoint',
        aws_access_key_id="AKIAYZLO52MXYI75GAG4",
        aws_secret_access_key="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",
        region_name="us-east-1"
    )

    try:
        cursor = conn.cursor()
        # cursor.execute("Create TABLE Gifts(id INT NOT NULL AUTO_INCREMENT, toId varchar(20), fromId varchar(20), vendor varchar(50), paymentId varchar(50), caption varchar(280), amount decimal(5,2), remaining decimal(5,2), PRIMARY KEY (id)) ")
        # TODO: checks - user same as auth token, balance greater than gift amount, card belongs to user
        
        toUser = ""
        cursor.execute("SELECT userId FROM Balance where phone = '" + body["toId"] + "'")
        row = cursor.fetchone()
        if row != None:
            toUser = row[0]

        cursor.execute("SELECT userId FROM Balance where phone = '" + body["fromId"] + "'")
        row = cursor.fetchone()
        fromUser = row[0]
        
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
            sqlCommand = "SELECT accessToken FROM Accounts where accountId = '" + body["paymentId"] + "'"
            cursor.execute(sqlCommand)
            row = cursor.fetchone()
            accessToken = row[0]
            stripeResponse = client.Processor.stripeBankAccountTokenCreate(accessToken, body["paymentId"])
            stripeToken = stripeResponse['stripe_bank_account_token']
            print(stripeToken)
            
            charge = stripe.Charge.create(
                amount=body["amount"]*100, # Stripe takes the amount in cents
                currency="usd",
                source=stripeToken,
                description="Gifty charge for " + body["vendor"],
            )
            
            print(charge)
        
        sqlCommand = "INSERT INTO Gifts(toUser,toId,fromUser,fromId,vendor,paymentId,caption,amount,remaining) VALUES ('%s','%s','%s','%s','%s','%s','%s',%.2f,%.2f)" % \
                     (toUser, body["toId"], fromUser, body["fromId"], body["vendor"], body["paymentId"], body["caption"], body["amount"], body["amount"])
        print(sqlCommand)
        cursor.execute(sqlCommand)
        
        cursor.execute("SELECT token FROM DeviceTokens WHERE user = '%s'" % (toUser))
        row_count = cursor.rowcount
        if row_count == 0:
            # send text
            response = client.send_messages(
                ApplicationId='bb5e579f87c34a5abf30677a1b766ce6',
                MessageRequest={
                    'Addresses': {
                        body["toId"]: {
                            'ChannelType': 'SMS'
                        }
                    },
                    'MessageConfiguration': {
                        'SMSMessage': {
                            'Body': body["fromId"] + " sent you a gift to " + body["vendor"],
                            'MessageType': "TRANSACTIONAL"
                        }
                    }
                }
            )
        else:
            row = cursor.fetchone()

            token=row[0]
            
            message_request = {
                'Addresses': {
                    token: {
                        'ChannelType': 'APNS_SANDBOX'
                    }
                },
                'MessageConfiguration': {
                    'APNSMessage': {
                        'Action': "OPEN_APP",
                        'Body': (body["caption"]),
                        'Priority' : "normal",
                        'SilentPush': False,
                        'Title': body["fromId"] + " sent you a gift to " + body["vendor"]
                    }
                }
            }
            
            response = client.send_messages(
                ApplicationId='bb5e579f87c34a5abf30677a1b766ce6',
                MessageRequest=message_request
            )
        print("SUCCESS")
    except Exception as e:
        print("ERROR: " + str(e))
    finally:
        conn.close()

    return {
        'statusCode': 200
    }