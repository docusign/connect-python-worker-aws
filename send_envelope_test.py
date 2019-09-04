import unittest
import time
import os
from process_notification import current_directory
from create_envelope import *

class SendEnvelope(unittest.TestCase):
    @classmethod
    def test_send(cls):
        try:
            print("\nSending an envelope. The envelope includes HTML, Word, and PDF documents.\n" +
            "It takes about 15 seconds for DocuSign to process the envelope request...")
            result = send_envelope()
            print(f"Envelope status: {result.status}. Envelope ID: {result.envelope_id}")
            SendEnvelope.created()

        except IOError as e:
            print(f"Could not open the file: {e}")

        except docusign.ApiException as e:
            print("\nDocuSign Exception!")

    @classmethod
    def created(cls):
        time.sleep(30)
        if(not os.path.exists(current_directory + "\\output\\order_Test_Mode.pdf")):
            AssertionError()
        
if __name__ == '__main__':
    unittest.main()