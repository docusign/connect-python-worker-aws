# Python: Connect Worker for AWS

Repository: [connect-python-worker-aws](https://github.docusignhq.com/chen-ostrovski/connect-python-worker-aws.git)

## Introduction

This is an example worker application for
Connect webhook notification messages sent
via the [AWS SQS (Simple Queueing System)](https://aws.amazon.com/sqs/).

This application receives DocuSign Connect
messages from the queue and then processes them:

* If the envelope is complete, the application
  uses a DocuSign JWT Grant token to retrieve
  the envelope's combined set of documents,
  and stores them in the `output` directory.
  
   For this example, the envelope **must** 
   include an Envelope Custom Field
   named `Sales order.` The Sales order field is used
   to name the output file.

## Architecture

![Connect listener architecture](data/connect_listener_architecture.png)

AWS has [SQS](https://aws.amazon.com/tools/)
SDK libraries for C#, Java, Node.js, Python, Ruby, C++, and Go. 

## Installation

This example requires Python v3.6 or later.
The SDK itself works with Python v2.7 or later.

1. Install the example 
   [Connect listener for AWS](https://github.com/docusign/connect-node-listener-aws)
   on AWS.
   At the end of this step, you will have the
   `Queue URL`, `Queue Region` and `Enqueue url`.

2. Download or clone this repository. Then:

````
cd connect-python-worker-aws
pip install docusign_esign
````
3. Using AWS IAM, create an IAM `User` with access to your SQS queue.

4. Configure the **ds_config.ini** file: [ds_config.ini](ds_config.ini)
    The application uses the OAuth JWT Grant flow.

    If consent has not been granted to the application by
    the user, then the application provides a url
    that can be used to grant individual consent.

    **To enable individual consent:** either
    add the URL [https://www.docusign.com](https://www.docusign.com) as a redirect URI
    for the Integration Key, or add a different URL and
    update the `oAuthConsentRedirectURI` setting
    in the ds_config.ini file.

5.  Creating the Integration Key
    Your DocuSign Integration Key must be configured for a JWT OAuth authentication flow:
    * Create a public/private key pair for the key. Store the private key
    in a secure location. You can use a file or a key vault.
    * The example requires the private key. Store the private key in the
    [ds_config.ini](ds_config.ini) file.
  
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
 N7b6a66DYU8/0BwXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 7lBHBbJcc76v+18XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 jCt15ZT4aux//2ZXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 ....
 PEHgznlGh/vUboCXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 -----END RSA PRIVATE KEY-----
````  

## Run the examples

````
python aws_worker.py
````
## Testing
Configure a DocuSign Connect subscription to send notifications to
the Cloud Function. Create / complete a DocuSign envelope.
The envelope **must include an Envelope Custom Field named "Sales order".**

* Check the Connect logs for feedback.
* Check the console output of this app for log output.
* Check the `output` directory to see if the envelope's
  combined documents and CoC were downloaded.

  For this code example, the 
  envelope's documents will only be downloaded if
  the envelope is `complete` and includes a 
  `Sales order` custom field.

## Support, Contributions, License

Submit support questions to [StackOverflow](https://stackoverflow.com). Use tag `docusignapi`.

Contributions via Pull Requests are appreciated.
All contributions must use the MIT License.

This repository uses the MIT license, see the
[LICENSE](https://github.com/docusign/eg-01-Python-jwt/blob/master/LICENSE) file.
