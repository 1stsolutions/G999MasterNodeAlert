# Created:   November 1 2020
# (c) Copyright governed by MIT License.
# To edit: Add values wherever "ADD" is written 

import requests, json, time, datetime, smtplib, ssl, email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#Send Email
def sendEmail(output, address, recipientEmail, error):
    sender = 'ADD FROM EMAIL ADDRESS'  
    senderName = 'Masternode Alert'
    usernameSMTP = "ADD SMTP"
    passwordSMTP = "ADD PASSWORD"
    host = "ADD HOST SERVER"
    port = 587

    if error == 0:
        subject = "Master Node Update for " + address
        bodyText = """\
            Address: """ + address + """
            Last Seen: """ + str(output["lastSeen"]) + """ UTC
            Time Active: """ + str(output["activeTime"]) + """
            Last Paid: """ + str(output["lastPaid"]) + """ UTC
            Country: """ + str(output["country"]) + """
            Status: """ + str(output["status"]) + """

            Your total received is: """ + str(output["received"]) + """
            Your total sent is: """ + str(output["sent"]) + """
            Your current balance (including 749,999 stake) is: """ + str(output["balance"]) + """
            Available balance from this node is """ + str(output["available"]) + """
            
            For questions and concerns about Master Nodes, check out the G999 Masternode Discord Server.
        """
        bodyHTML = """<html>
            <body>
                <p style="font-size: 16px; font-family: Arial, sans-serif;">
                Address: """ + address + """<br>
                Last Seen: """ + str(output["lastSeen"]) + """ UTC<br>
                Time Active: """ + str(output["activeTime"]) + """<br>
                Last Paid: """ + str(output["lastPaid"]) + """ UTC<br>
                Country: """ + str(output["country"]) + """<br>
                Status: """ + str(output["status"]) + """<br><br>
                Total received is: """ + str(output["received"]) + """<br>
                Total sent is: """ + str(output["sent"]) + """<br>
                Current balance (including 749,999 stake) is: """ + str(output["balance"]) + """<br>
                Available balance from this node is """ + str(output["available"]) + """<br></p>
                <p style="font-size: 13px; font-family: Arial, sans-serif;">
                Please note that if you have multiple masternodes in one wallet, this available balance will not be the complete amount.<br>
                For questions and concerns about Master Nodes, check out the G999 Masternode Discord Server</p> 
            </body>
            </html>
            """
    if error == 1:
        subject = "Emergency Alert for " + address
        bodyText = """\
            Unable to find """ + address + """
            Check with your VPS provider IMMEDIATELY to make sure it is running. 
        """
        bodyHTML = """\
        <html>
        <body>
            <p style="font-size: 16px; font-family: Arial, sans-serif;">Unable to find """ + address + """<br></p>
            <p style="font-size: 20px; font-family: Arial, sans-serif; color:red">Check with your VPS provider IMMEDIATELY to makes sure it is running.</p>
        </body>
        </html>
        """

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = email.utils.formataddr((senderName, sender))
    msg['To'] = recipientEmail

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(bodyText, 'plain')
    part2 = MIMEText(bodyHTML, 'html')

    # Attach parts into message container.
    msg.attach(part1)
    msg.attach(part2)

    # Try to send the message.
    try:  
        server = smtplib.SMTP(host, port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(usernameSMTP, passwordSMTP)
        server.sendmail(sender, recipientEmail, msg.as_string())
        server.close()
    # Display an error message if something goes wrong.
    except Exception as e:
        print ("Error: ", e)
    else:
        print ("Email sent!")

# Get the master nodes
getMasterNodes = requests.get('https://explorer.g999main.net/ext/getmasternodes/')
data = getMasterNodes.json()

# Function to check address
def checkAddress(address,recipientEmail):
    x = 0
    error = 1
    for z in data["data"]:
        addr = data["data"][x]["addr"]
        if(addr == address):
            output = {}
            lastSeen = data["data"][x]["lastseen"]
            output["lastSeen"] = datetime.datetime.fromtimestamp(lastSeen)
            activeTime = data["data"][x]["activetime"]
            output["activeTime"] = datetime.timedelta(seconds =activeTime)
            lastPaid = data["data"][x]["lastpaid"]
            output["lastPaid"] = datetime.datetime.fromtimestamp(lastPaid)
            output["country"] = data["data"][x]["country"]
            output["status"] = data["data"][x]["status"]
            getDetails = requests.get('https://explorer.g999main.net/ext/getaddress/' + address)
            details = getDetails.json()
            output["details"] = getDetails.json()
            output["balance"] = details["balance"]
            output["sent"] = details["sent"]
            output["received"] = details["received"]
            output["available"] =  float(details["balance"]) - 749999 #The Masternode Stake amount
            error = 0
            sendEmail(output, address, recipientEmail, error)
        x += 1
    if(error == 1):
        output = 0
        sendEmail(output, address, recipientEmail, error)
		
#Implementation: Run locally using checkAddress function or on a AWS lambda using the lambda_handler function
checkAddress("ADD PUBLIC KEY","ADD TO EMAIL ADDRESS") 
 
def lambda_handler(event, context):
    checkAddress(event["address"],event["recipientEmail"])
    return
