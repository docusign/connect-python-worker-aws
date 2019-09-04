import configparser
import itertools
import os

class DSConfig:
 
    instance = None
    config = {}

    @staticmethod
    def getInstance():
        if DSConfig.instance is None:
            instance = DSConfig()

        return instance

    def __init__(self):
        client_id = os.environ.get('DS_CLIENT_ID', None)
        if client_id is not None:
            self.config["DS_CLIENT_ID"] = client_id
            self.config["DS_AUTH_SERVER"] = os.environ.get("DS_AUTH_SERVER")
            self.config["DS_IMPERSONATED_USER_GUID"] = os.environ.get("DS_IMPERSONATED_USER_GUID")
            self.config["DS_TARGET_ACCOUNT_ID"] = os.environ.get("DS_TARGET_ACCOUNT_ID")
            self.config["DS_SIGNER_EMAIL"] = os.environ.get("DS_SIGNER_EMAIL")
            self.config["DS_SIGNER_NAME"] = os.environ.get("DS_SIGNER_NAME")
            self.config["DS_CC_EMAIL"] = os.environ.get("DS_CC_EMAIL")
            self.config["DS_CC_NAME"] = os.environ.get("DS_CC_NAME")
            self.config["DS_PRIVATE_KEY"] = os.environ.get("DS_PRIVATE_KEY")
            self.config["QUEUE_URL"] = os.environ.get("QUEUE_URL")
            self.config["AWS_ACCOUNT"] = os.environ.get("AWS_ACCOUNT")
            self.config["AWS_SECRET"] = os.environ.get("AWS_SECRET")
            self.config["BASIC_AUTH_NAME"] = os.environ.get("BASIC_AUTH_NAME")
            self.config["BASIC_AUTH_PW"] = os.environ.get("BASIC_AUTH_PW")
            self.config["QUEUE_REGION"] = os.environ.get("QUEUE_REGION")
            self.config["DEBUG"] = os.environ.get("DEBUG")
            self.config["ENVELOPE_CUSTOM_FIELD"] = os.environ.get("ENVELOPE_CUSTOM_FIELD")
            self.config["OUTPUT_FILE_PREFIX"] = os.environ.get("OUTPUT_FILE_PREFIX")
            self.config["ENABLE_BREAK_TEST"] = os.environ.get("ENABLE_BREAK_TEST")
            self.config["TEST_ENQUEUE_URL"] = os.environ.get("TEST_ENQUEUE_URL")
        else:
            ini_file = 'ds_config.ini'
            if os.path.isfile(ini_file):
                config_parser = configparser.ConfigParser()
                with open(ini_file) as fp:
                    # Enable ini file to not have explicit global section
                    config_parser.read_file(itertools.chain(['[global]'], fp), source=ini_file)
                self.config = config_parser['global']
            else:
                raise Exception(f"Missing config file |{ini_file}| and environment variables are not set.")

    def _get_key(self,str):
        return self.config[str]

    @staticmethod
    def get_key(str):
        return DSConfig.getInstance()._get_key(str)

    @staticmethod
    def aud():
        auth_server = DSConfig.getInstance().get_key("DS_AUTH_SERVER")

        if 'https://' in auth_server:
            aud = auth_server[8:]
        else: # assuming http://blah
            aud = auth_server[7:]

        return aud

    @staticmethod
    def api():
        return "restapi/v2"

    @staticmethod
    def permission_scopes():
        return "signature impersonation"

    @staticmethod
    def jwt_scope():
        return "signature"

    