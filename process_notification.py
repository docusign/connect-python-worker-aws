import xml.etree.ElementTree as ET
import docusign_esign as docusign
import re
import os
import sys
import subprocess
from datetime import datetime
from jwt_auth import *
from ds_config_files import ds_config
from docusign_esign import EnvelopesApi, ApiException

current_directory = os.getcwd()

# Process the notification message
def process(test, xml):
    # Send the message to the test mode
    if(not test == ""):
        processTest(test)

    # In test mode there is no xml sting, should be checked before trying to parse it
    if(not xml == ""):
        # Step 1. parse the xml
        root = ET.fromstring(xml)
        # get the namespace from the xml
        def get_namespace(element):
            ns = re.match(r'\{.*\}', element.tag)
            return ns.group(0) if ns else ''
        nameSpace = get_namespace(root)

        # Extract from the XML the fields values
        envelopeId = root.find(f'{nameSpace}EnvelopeStatus/{nameSpace}EnvelopeID').text
        subject = root.find(f'{nameSpace}EnvelopeStatus/{nameSpace}Subject').text
        senderName = root.find(f'{nameSpace}EnvelopeStatus/{nameSpace}UserName').text
        senderEmail = root.find(f'{nameSpace}EnvelopeStatus/{nameSpace}Email').text
        status = root.find(f'{nameSpace}EnvelopeStatus/{nameSpace}Status').text
        created =  root.find(f'{nameSpace}EnvelopeStatus/{nameSpace}Created').text
        orderNumber = root.find(f'{nameSpace}EnvelopeStatus/{nameSpace}CustomFields/{nameSpace}CustomField/{nameSpace}Value').text

        if(status == "Completed"):
            completedMsg = "Completed: True"
        else:
            completedMsg = ""

        # For debugging, you can print the entire notification
        print("EnvelopeId: {}".format(envelopeId))
        print("Subject: {}".format(subject))
        print("Sender: {}, {}".format(senderName, senderEmail))
        print("Order Number: {}".format(orderNumber))
        print("Status: {}".format(status))
        print("Sent: {}, {}".format(created, completedMsg))

        # Step 2. Filter the notifications
        ignore = False
        # Check if the envelope was sent from the test mode 
        # If sent from test mode - ok to continue even if the status not equals to Completed
        if(not orderNumber == "Test_Mode"):
            if(not status == "Completed"):
                ignore = True
                if(ds_config("DEBUG") == "True"):
                    print("{} IGNORED: envelope status is {}".format(datetime.now(), status))
            
        if(orderNumber == None or orderNumber == ""):
            ignore = True
            if(ds_config("DEBUG") == "True"):
                print("{} IGNORED: envelope does not have a {} envelope custom field.".format(datetime.now(), ds_config("ENVELOPE_CUSTOM_FIELD")))
            
        # Step 3. (Future) Check that this is not a duplicate notification
        # The queuing system delivers on an "at least once" basis. So there is a 
        # chance that we have already processes this notification.
        #
        # For this example, we'll just repeat the document fetch if it is duplicate notification

        # Step 4 save the document - it can raise an exception which will be caught at startQueue 
        if(not ignore):
            saveDoc(envelopeId, orderNumber)

# Creates a new file that contains the envelopeId and orderNumber
def saveDoc(envelopeId, orderNumber):
    try:
        api_client.set_default_header("Authorization", "Bearer " + api_client.token)
        accountID = get_account_id()
        envelope_api = EnvelopesApi(api_client)
        
        results_file = envelope_api.get_document(accountID , "combined" , envelopeId)

        # Create the output directory if needed
        output_directory = os.path.join(current_directory, r'output')
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            if(not os.path.exists(output_directory)):
                print("{} Failed to create directory".format(datetime.now()))

        filePath = current_directory + "\\output" + "\\" + ds_config("OUTPUT_FILE_PREFIX") + orderNumber + ".pdf"
        # Save the results file in the output directory and change the name of the file
        os.rename(results_file,filePath)
        
    # Create a file
    except ApiException as e:
        print("{} API exception: {}. saveDoc error".format(datetime.now(), e))

        # Catch exception while fetching and saving docs for envelope
    except Exception as e:
        print("{} Error while fetching and saving docs for envelope {}, order {}".format(datetime.now(), envelopeId, orderNumber))
        print("{} saveDoc error {}".format(datetime.now(), e))

# Process test details into files
def processTest(test):
    # Exit the program if BREAK_TEST equals to true or if orderNumber contains "/break"
    if(ds_config("ENABLE_BREAK_TEST") == "True" and "/break" in ("" + test)):
        print("{} BREAKING worker test!".format(datetime.now()))
        sys.exit(2)

    print("{} Processing test value {}".format(datetime.now(), test))

    # Create the test directory if needed
    test_directory = os.path.join(current_directory, r'test_messages')
    if not os.path.exists(test_directory):
        os.makedirs(test_directory)
        if(not os.path.exists(test_directory)):
            print("{} Failed to create directory".format(datetime.now()))

    # First shuffle test1 to test2 (if it exists) and so on
    for i in range(9,0,-1):
        old_File_path = test_directory + "\\test" + str(i) + ".txt"
        new_File_path = test_directory + "\\test" + str(i+1) + ".txt"
        # If the old file exists
        if(os.path.exists(old_File_path)):
            # If the new file exists - remove it 
            if(os.path.exists(new_File_path)):
                os.remove(new_File_path)
            # Rename the file name - only works if new_File_path does not exist 
            os.rename(old_File_path, new_File_path)

    # The new test message will be placed in test1 - creating new file
    newFile= open(test_directory + "\\test1.txt","w+")
    newFile.write(test)
    print("{} New file created".format(datetime.now()))
    newFile.close