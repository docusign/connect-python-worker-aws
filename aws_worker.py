import docusign_esign as docusign
import time
import boto3
import json
import queue
import sys
from date_pretty import date
from process_notification import process
from jwt_auth import *
from ds_config_files import ds_config
sqs = boto3.client('sqs', region_name=ds_config("QUEUE_REGION"), aws_access_key_id = ds_config("AWS_ACCOUNT"), aws_secret_access_key = ds_config("AWS_SECRET"))
checkLogQ = queue.Queue()
restart = True

def main():
    listenForever()

# The function will listen forever, dispatching incoming notifications
# to the processNotification library. 
# See https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/sqs-examples-send-receive-messages.html#sqs-examples-send-receive-messages-receiving 
def listenForever():
    # Check that we can get a DocuSign token
    testToken()
    while(True):
        global restart
        if(restart):
            print(date() + "Starting queue worker")
            restart = False
            # Start the queue worker
            startQueue()
        time.sleep(5)    

# Check that we can get a DocuSign token and handle common error
# cases: ds_configuration not configured, need consent.
def testToken():
    try:
        if(ds_config("DS_CLIENT_ID") == "{CLIENT_ID}"):
            print(date() + "Problem: you need to configure this example, either via environment variables (recommended)\n"
                "or via the ds_configuration.js file.\n"
                "See the README file for more information\n")

        check_token()

    # An API problem
    except docusign.ApiException as e:
        print("\n\nDocuSign Exception!")
        # Special handling for consent_required
        body = e.body.decode('utf8')
        if("consent_required" in body):
            consent_scopes = "signature%20impersonation"
            consent_redirect_URL = "https://www.docusign.com"
            consent_url = "{}/oauth/auth?response_type=code&scope={}&client_id={}&redirect_uri={}".format(ds_config("DS_AUTH_SERVER"), consent_scopes, ds_config("DS_CLIENT_ID"),consent_redirect_URL)
            print(f"""\nC O N S E N T   R E Q U I R E D
            Ask the user who will be impersonated to run the following url:
            {consent_url}
            It will ask the user to login and to approve access by your application.
            Alternatively, an Administrator can use Organization Administration to
            pre-approve one or more users.""")
            sys.exit(0)

        else:
            # Some other DocuSign API problem
            print (f"   Reason: {e.reason}")
            print (f"   Error response: {e.body.decode('utf8')}")
            sys.exit(0)

    # Not an API problem
    except Exception as e:
        print(date() + e)

# Receive and wait for messages from queue      
def startQueue():
    
    # Maintain the array checkLogQ as a FIFO buffer with length 4.
    # When a new entry is added, remove oldest entry and shuffle.
    def addCheckLogQ(message):
        length = 4
        # If checkLogQ size is smaller than 4 add the message
        if(checkLogQ.qsize() < length):
            checkLogQ.put(message)
        # If checkLogQ size is bigger than 4    
        else:
            # Remove the oldest message and add the new one
            checkLogQ.get()
            checkLogQ.put(message)

    # Prints all checkLogQ messages to the console  
    def printCheckLogQ():
    # Prints and Deletes all the elements in the checkLogQ
        for index in range(checkLogQ.qsize()):
            print(checkLogQ.get())

    try:
        while(True):
            # Receive messages from queue, maximum waits for 20 seconds for message
            # receive_request - contain all the queue messages
            receive_request = (sqs.receive_message(QueueUrl=ds_config("QUEUE_URL"), WaitTimeSeconds=20, MaxNumberOfMessages=10)).get("Messages")
            addCheckLogQ(date() +"Awaiting a message...")
            # If receive_request is not None (when message is received)
            if(receive_request is not None):
                msgCount = len(receive_request)
            else:
                msgCount=0
            addCheckLogQ(date() +"found {} message(s)".format(msgCount))
            # If at least one message has been received
            if(msgCount):
                printCheckLogQ()
                for message in receive_request:
                    messageHandler(message)

    # Catches all types of errors that may occur during the program
    except Exception as e:
        printCheckLogQ()
        print(date() + "Queue receive error: {}".format(e))
        time.sleep(5)
        # Restart the program
        global restart
        restart = True
           
# Process a message
# See https://github.com/Azure/azure-sdk-for-js/tree/master/sdk/servicebus/service-bus#register-message-handler
def messageHandler(message):
    if(ds_config("DEBUG") == "True"):
        print(date() + "Processing message id: {}".format(message["MessageId"]))

    try:
        # Creates a Json object from the message body
        body = json.loads(message["Body"])
    except Exception as e:
        body = False

    if(body):
        # Parse the information from message body. the information contains contains fields like test and xml
        test = body["test"]
        xml = body["xml"]
        process(test, xml)   
    else:
        print(date() + "Null or bad body in message id {}. Ignoring.".format(message["MessageId"]))
        
    # Delete received message from queue
    sqs.delete_message(QueueUrl=ds_config("QUEUE_URL"),ReceiptHandle=message["ReceiptHandle"])

if __name__ == '__main__':
    main()