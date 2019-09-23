import unittest
import time
import os
import urllib.request
import base64
from pathlib import Path
from datetime import datetime, timedelta
from process_notification import current_directory
from ds_config_files import ds_config
from date_pretty import date

class RunTest(unittest.TestCase):

    timeCheckNumber=0
    timeChecks = []
    modeName = "Select at the bottom of the file" # many or few
    successes = 0
    enqueueErrors = 0
    dequeueErrors = 0
    testsSent = []
    foundAll = False

    @classmethod
    def test_run(cls):
        for index in range(8):
            RunTest.timeChecks.append(datetime.now() + timedelta(hours=index+1))
        print(date() + "Starting")
        RunTest.doTests()
        print(date()  + "Done")

    @classmethod
    def doTests(cls):
        while(RunTest.timeCheckNumber <= 7):
            while(RunTest.timeChecks[RunTest.timeCheckNumber]>datetime.now()):
                RunTest.doTest()
                if(RunTest.modeName == "few"):
                    seconds_to_sleep = (RunTest.timeChecks[RunTest.timeCheckNumber] - datetime.now() + timedelta(minutes=2)).seconds
                    time.sleep(seconds_to_sleep)
            RunTest.showStatus()
            RunTest.timeCheckNumber += 1
        RunTest.showStatus()

    @classmethod
    def showStatus(cls):
        rate = (100.0 * RunTest.successes) / (RunTest.enqueueErrors + RunTest.dequeueErrors + RunTest.successes)
        print("#### Test statistics: {} ({}%) successes, {} enqueue errors, {} dequeue errors.".format(RunTest.successes, ("%.2f" % rate), RunTest.enqueueErrors, RunTest.dequeueErrors))

    @classmethod       
    def doTest(cls):
        RunTest.send() #Sets testSent
        endTime = datetime.now() + timedelta(minutes=3)
        RunTest.foundAll = False
        tests = len(RunTest.testsSent)
        successesStart = RunTest.successes
        while(not RunTest.foundAll and endTime>datetime.now()):
            time.sleep(1)
            RunTest.checkResults() # Sets foundAll and updates testsSent
        if(not RunTest.foundAll):
            RunTest.dequeueErrors += len(RunTest.testsSent)
        print("Test: {} sent, {} successes, {} failures.".format(tests, RunTest.successes-successesStart,len(RunTest.testsSent)))

    # Look for the reception of the testsSent values
    @classmethod
    def checkResults(cls):
        testsReceived = []
        file_data = ""
        for i in range(20):
            file_data=""
            try:
                # The path of the files created of Test mode
                testOutputDirPath = os.path.join(current_directory, "test_messages",  "test" + str(i) + ".txt")
                test_file = Path(testOutputDirPath) 
                if test_file.is_file():
                    with open(test_file) as f:
                        file_data = f.readlines()
                        testsReceived.append(file_data[0])
                        f.close()

            except IOError as e:
                print(f"Could not open the file: {e}")

            except OSError as e:
                print(f"OSError {e}")
            
            # Create a private copy of testsSent (testsSentOrig) and reset testsSent
            # Then, for each element in testsSentOrig not found, add back to testsSent.
            testsSentOrig = []
            testsSentOrig.extend(RunTest.testsSent)
            RunTest.testsSent.clear()
            for testValue in testsSentOrig:
                if testValue in testsReceived:
                    RunTest.successes += 1
                else:
                    RunTest.testsSent.append(testValue)
            # Update foundAll
            RunTest.foundAll = len(RunTest.testsSent)==0

    # Send 5 messages
    @classmethod
    def send(cls):
        RunTest.testsSent.clear()
        for i in range(5):
            try:
                now = time.time_ns() // 1000000
                testValue = "" + str(now)
                RunTest.send1(testValue)
                RunTest.testsSent.append(testValue)
            except Exception as e:
                RunTest.enqueueErrors += 1
                print(f"send: Enqueue error: {e}")
                time.sleep(30)
        
    # Send one enqueue request. Errors will be caught by caller
    @classmethod
    def send1(cls, test):
        try:
            time.sleep(0.5)
            url = ds_config("ENQUEUE_URL") + "?test=" + test
            request = urllib.request.Request(url)
            request.method = "GET"
            auth = RunTest.authObject()
            if(auth):
                base64string = base64.b64encode (bytes(auth, "utf-8"))
                request.add_header("Authorization", "Basic %s" % base64string.decode("utf-8")) 
            response = urllib.request.urlopen(request)
            if(response.getcode() is not 200):
                print("send1: GET not worked, StatusCode= {}".format(response.getcode()))
            response.close()

        except Exception as e:
            print(f"send1: https error: {e}")

    # Returns a string for the HttpsURLConnection request
    @classmethod
    def authObject(cls):
        if(not ds_config("BASIC_AUTH_NAME") is None and not ds_config("BASIC_AUTH_NAME") == "{BASIC_AUTH_NAME}" 
            and not ds_config("BASIC_AUTH_PW") is None and not ds_config("BASIC_AUTH_PW") == "{BASIC_AUTH_PS}"):
            return ds_config("BASIC_AUTH_NAME") + ":" + ds_config("BASIC_AUTH_PW")
        else:
            return False

if __name__ == '__main__':
    # choose the test mode: many - for many tests. few - for 5 tests every hour
    RunTest.modeName = "few"
    unittest.main()