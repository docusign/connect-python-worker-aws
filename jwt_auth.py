import time
import base64
import docusign_esign as docusign
from docusign_esign import EnvelopesApi, ApiException
from datetime import datetime, timedelta
from ds_config_files import ds_config, aud
#from .auth.oauth import OAuthUserInfo, OAuthToken, OAuth, Account, Organization, Link

TOKEN_REPLACEMENT_IN_SECONDS = 10 * 60
TOKEN_EXPIRATION_IN_SECONDS = 3600

api_client =  docusign.ApiClient()
account = None
_token_received = None
expiresTimestamp = 0

def check_token():
    current_time = int(round(time.time()))
    if not _token_received \
            or ((current_time + TOKEN_REPLACEMENT_IN_SECONDS) > expiresTimestamp):
        update_token()

def update_token():
    print ("Requesting an access token via JWT grant...", end='')
    private_key_bytes = str.encode(ds_config("DS_PRIVATE_KEY"))
    token = api_client.request_jwt_user_token(ds_config("DS_CLIENT_ID"), ds_config("DS_IMPERSONATED_USER_GUID"), aud(), private_key_bytes, TOKEN_EXPIRATION_IN_SECONDS)
    global account
    if account is None:
        account = get_account_info(api_client)
    base_uri = account['base_uri'] + '/restapi'
    api_client.host = base_uri
    api_client.token = token.access_token
    _token_received = True
    expiresTimestamp = (int(round(time.time())) + TOKEN_EXPIRATION_IN_SECONDS)
    print ("\nDone. Continuing...")

def get_account_id():
    return account['account_id']

def get_account_info(client):
    client.host = ds_config("DS_AUTH_SERVER")
    response = client.call_api("/oauth/userinfo", "GET", response_type="object")

    if len(response) > 1 and 200 > response[1] > 300:
        raise Exception("can not get user info:" ) # %d".format(response[1])

    accounts = response[0]['accounts']
    target = ds_config("DS_TARGET_ACCOUNT_ID")

    if target is None or target == "FALSE":
        # Look for default
        for acct in accounts:
            if acct['is_default']:
                return acct

    # Look for specific account
    for acct in accounts:
        if acct['account_id'] == target:
            return acct

    raise Exception(f"\n\nUser does not have access to account {target}\n\n")

