# -*- coding: utf-8 -*-
# coding: utf-8
import base64
from os import path
from docusign_esign import EnvelopesApi, EnvelopeDefinition, Signer, CarbonCopy, SignHere, Tabs, Recipients, Document, TextCustomField, CustomFields
from ds_config_files import *
from jwt_auth import *

demo_docs_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), 'data'))
DOC_2_DOCX = "World_Wide_Corp_Battle_Plan_Trafalgar.docx"
DOC_3_PDF = "World_Wide_Corp_lorem.pdf"
envelope_id = None
status = None

def send_envelope():
    check_token()

    # document 1 (html) has sign here anchor tag **signature_1**
    # document 2 (docx) has sign here anchor tag /sn1/
    # document 3 (pdf)  has sign here anchor tag /sn1/
    #
    # The envelope has two recipients.
    # recipient 1 - signer
    # recipient 2 - cc
    # The envelope will be sent first to the signer.
    # After it is signed, a copy is sent to the cc person.

    args = {
        'signer_email': ds_config("DS_SIGNER_EMAIL"),
        'signer_name': ds_config("DS_SIGNER_NAME"),
        'cc_email':ds_config("DS_CC_EMAIL"),
        'cc_name': ds_config("DS_CC_NAME"),
    }

    # create the envelope definition
    env = EnvelopeDefinition(
        email_subject='Document sent from the Test Mode'
    )
    doc1_b64 = base64.b64encode(
        bytes(create_document1(args), 'utf-8')).decode('ascii')
    # read files 2 and 3 from a local directory
    # The reads could raise an exception if the file is not available!
    with open(path.join(demo_docs_path, DOC_2_DOCX),
                "rb") as file:
        doc2_docx_bytes = file.read()
    doc2_b64 = base64.b64encode(doc2_docx_bytes).decode('ascii')
    with open(path.join(demo_docs_path, DOC_3_PDF),
                "rb") as file:
        doc3_pdf_bytes = file.read()
    doc3_b64 = base64.b64encode(doc3_pdf_bytes).decode('ascii')

    # Create the document models
    document1 = Document(  # create the DocuSign document object
        document_base64=doc1_b64,
        name='Order acknowledgement',
        # can be different from actual file name
        file_extension='html',  # many different document types are accepted
        document_id='1'  # a label used to reference the doc
    )
    document2 = Document(  # create the DocuSign document object
        document_base64=doc2_b64,
        name='Battle Plan',  # can be different from actual file name
        file_extension='docx',  # many different document types are accepted
        document_id='2'  # a label used to reference the doc
    )
    document3 = Document(  # create the DocuSign document object
        document_base64=doc3_b64,
        name='Lorem Ipsum',  # can be different from actual file name
        file_extension='pdf',  # many different document types are accepted
        document_id='3'  # a label used to reference the doc
    )
    # The order in the docs array determines the order in the envelope
    env.documents = [document1, document2, document3]

    # Create the signer recipient model
    signer1 = Signer(
        email=args['signer_email'], name=args['signer_name'],
        recipient_id="1", routing_order="1"
    )
    # routingOrder (lower means earlier) determines the order of deliveries
    # to the recipients. Parallel routing order is supported by using the
    # same integer as the order for two or more recipients.

    # create a cc recipient to receive a copy of the documents
    cc1 = CarbonCopy(
        email=args['cc_email'], name=args['cc_name'],
        recipient_id="2", routing_order="2")

    # Create signHere fields (also known as tabs) on the documents,
    # We're using anchor (autoPlace) positioning
    #
    # The DocuSign platform searches throughout your envelope's
    # documents for matching anchor strings. So the
    # signHere2 tab will be used in both document 2 and 3 since they
    #  use the same anchor string for their "signer 1" tabs.
    sign_here1 = SignHere(
        anchor_string='**signature_1**', anchor_units='pixels',
        anchor_y_offset='10', anchor_x_offset='20')
    sign_here2 = SignHere(
        anchor_string='/sn1/', anchor_units='pixels',
        anchor_y_offset='10', anchor_x_offset='20')

    # Add the tabs model (including the sign_here tabs) to the signer
    # The Tabs object wants arrays of the different field/tab types
    signer1.tabs = Tabs(sign_here_tabs=[sign_here1, sign_here2])

    # Add the recipients to the envelope object
    recipients = Recipients(signers=[signer1], carbon_copies=[cc1])
    env.recipients = recipients

    # Request that the envelope be sent by setting |status| to "sent".
    # To request that the envelope be created as a draft, set to "created"
    env.status = "sent"

    # Creates the Salse order Custom Field
    text_custom_field = TextCustomField(name='Sales order', value='Test_Mode', show='true',
                                    required='true')
    custom_fields = CustomFields(text_custom_fields=[text_custom_field])
    env.custom_fields = custom_fields

    envelope_api = EnvelopesApi(api_client)
    results = envelope_api.create_envelope(get_account_id(), envelope_definition=env)

    return results

def create_document1(args):
    """ Creates document 1 -- an html document"""

    return f"""
    <!DOCTYPE html>
    <html>
        <head>
          <meta charset="UTF-8">
        </head>
        <body style="font-family:sans-serif;margin-left:2em;">
        <h1 style="font-family: 'Trebuchet MS', Helvetica, sans-serif;
            color: darkblue;margin-bottom: 0;">World Wide Corp</h1>
        <h2 style="font-family: 'Trebuchet MS', Helvetica, sans-serif;
          margin-top: 0px;margin-bottom: 3.5em;font-size: 1em;
          color: darkblue;">Order Processing Division</h2>
        <h4>Ordered by {args['signer_name']}</h4>
        <p style="margin-top:0em; margin-bottom:0em;">Email: {args['signer_email']}</p>
        <p style="margin-top:0em; margin-bottom:0em;">Copy to: {args['cc_name']}, {args['cc_email']}</p>
        <p style="margin-top:3em;">
    Candy bonbon pastry jujubes lollipop wafer biscuit biscuit. Topping brownie sesame snaps sweet roll pie. Croissant danish biscuit soufflé caramels jujubes jelly. Dragée danish caramels lemon drops dragée. Gummi bears cupcake biscuit tiramisu sugar plum pastry. Dragée gummies applicake pudding liquorice. Donut jujubes oat cake jelly-o. Dessert bear claw chocolate cake gummies lollipop sugar plum ice cream gummies cheesecake.
        </p>
        <!-- Note the anchor tag for the signature field is in white. -->
        <h3 style="margin-top:3em;">Agreed: <span style="color:white;">**signature_1**/</span></h3>
        </body>
    </html>
    """
