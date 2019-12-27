import json
import pymysql
import plaid

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

    try:
        cursor = conn.cursor()
        # cursor.execute("Create TABLE Accounts(user varchar(50), phone varchar(20), bank varchar(50), accessToken varchar(100),stripeToken varchar(50),accountId varchar(50),accountMask varchar(4),accountName varchar(50),accountType varchar(50),accountSubtype varchar(50)) ")
        
        # TODO: if bank already exists for user, just update accessToken
        response = client.Item.public_token.exchange(body["accessToken"])
        accessToken = response['access_token']
        sqlCommand = "INSERT INTO Accounts(user,phone,bank,accessToken,accountId,accountMask,accountName,accountType,accountSubtype) VALUES "
        
        accounts = body["accounts"]
        for account in accounts:
            stripeResponse = client.Processor.stripeBankAccountTokenCreate(accessToken, account["id"])
            stripeToken = stripeResponse['stripe_bank_account_token']
            # TODO: if accessToken is not sandbox, use stripe token to modify connected account with bank account
            
            sqlCommand = sqlCommand + "('%s','%s','%s','%s','%s','%s','%s','%s','%s')," % \
                (body["username"], body["phone"], body["bankName"], accessToken, account["id"], account["mask"], account["name"], account["type"], account["subtype"])
        sqlCommand = sqlCommand[:-1] + ";"
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