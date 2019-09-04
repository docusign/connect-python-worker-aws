# Example 1: Python Service Integration

Repository: [eg-01-Python-jwt](https://github.com/docusign/eg-01-Python-jwt)

<!--
## Articles and Screencasts

* Guide: Using OAuth JWT flow with DocuSign.
* Screencast: Using OAuth JWT flow with DocuSign.
* Guide: Sending an envelope with the Node.JS SDK.
* Screencast: Sending an example with Node.JS SDK.
-->

## Introduction

This software is an example of a **System Integration**.
This type of application interacts with DocuSign on its
own. There is no user interface and no user is present
during normal operation.

The application uses the OAuth JWT grant flow to impersonate
a user in the account.

This launcher example includes two examples:
1. Send an html, Word, and PDF file in an envelope to be signed.
1. List the envelopes in the account whose status 
   changed in the last 30 days.

## Installation

This example requires Python v3.6 or later.
The SDK itself works with Python v2.7 or later.

Download or clone this repository. Then:

````
cd eg-01-Python-jwt
pip install docusign_esign
````

### Configure the example's settings

Configure the **ds_config.ini** file:

#### Creating the Integration Key
Your DocuSign Integration Key must be configured for a JWT OAuth authentication flow:
* Create a public/private key pair for the key. Store the private key
  in a secure location. You can use a file or a key vault.
* The example requires the private key. Store the private key in the
  `ds_config.ini` file.
    
  **Note:** the private key's second and subsequent
  lines need to have a space added at the beginning due
  to requirements from the Python configuration file
  parser. Example:
   
````
# private key string
# NOTE: the Python config file parser requires that you 
# add a space at the beginning of the second and
# subsequent lines of the multiline key value:  
DS_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----
 N7b6a66DYU8/0BwH47oJA7lBHBbJcc76v+1892cCgYEArtQjCt15ZT4aux//2ZWD
 ....
 PEHgznlGh/vUboCuA4tQOcKytxFfKG4F+jM/g4GH9z46KZOow3Hb6g==
 -----END RSA PRIVATE KEY-----
````   

* If you will be using individual permission grants, you must create a
  `Redirect URI` for the key. Any URL can be used. By default, this
  example uses `https://www.docusign.com`


#### The impersonated user's guid
The JWT will impersonate a user within your account. The user can be
an individual or a user representing a group such as "HR".

The example needs the guid assigned to the user.
The guid value for each user in your account is available from
the Administration tool in the **Users** section.

To see a user's guid, **Edit** the user's information.
On the **Edit User** screen, the guid for the user is shown as
the `API Username`.

## Run the examples

````
python main.py
````

## Support, Contributions, License

Submit support questions to [StackOverflow](https://stackoverflow.com). Use tag `docusignapi`.

Contributions via Pull Requests are appreciated.
All contributions must use the MIT License.

This repository uses the MIT license, see the
[LICENSE](https://github.com/docusign/eg-01-Python-jwt/blob/master/LICENSE) file.
