import pysftp as sftp
import smtplib
import ssl
import yaml
import logging
import time

startTime = time.time()

# Email/SMTP Info 
mailPort = 465
mailPass = "<Email Password>"
mailUser = "<Email Username>"
message = "Subject: sFTP Error\n\n"
server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.login(mailUser, mailPass)

# Create Log File and Exclusion File
try:
    log = open('logs.log', 'r')
    log.close()
except IOError as e:
    log = open('logs.log', 'w+')
    log.close()
try:
    excl = open('exclusion.txt', 'r')
    excl.close()
except IOError as e:
    excl = open('exclusion.txt', 'w+')
    excl.close()

logging.basicConfig(filename='logs.log', format='%(asctime)s %(message)s')

context = ssl.create_default_context()

cnopts = sftp.CnOpts()
cnopts.hostkeys = None


def sftpDl(mailMessage):

    with open("sites.yaml", 'r') as stream:
        try:
            doc = yaml.load(stream)

        except yaml.YAMLError as e:
            logging.critical(e)
            mailMessage += e
            print(e)
            return mailMessage

    for i in doc["connInfo"]:
        toAct = True
        hostname = doc["connInfo"][i]["hostname"]
        action = doc["connInfo"][i]["action"]
        username = doc["connInfo"][i]["username"]
        passKey = doc["connInfo"][i]["passKey"]
        source = doc["connInfo"][i]["source"]
        target = doc["connInfo"][i]["target"]

        try:
            exRead = open("exclusion.txt", "r")
            f1 = exRead.readlines()
            for x in f1:
                if x == (i + "\n"):
                    toAct = False
                    break
            exRead.close()

            if toAct:
                try:
                    s = sftp.Connection(host=hostname, username=username, password=passKey, cnopts=cnopts)
                except Exception as e:
                    s = sftp.Connection(host=hostname, username=username, private_key=passKey, cnopts=cnopts)
                if action == "down":
                    try:
                        s.get_r(source, target)
                    except Exception as e:
                        s.get(source, target)
                    logging.critical("Downloaded from " + source + " to " + target)
                elif action == "up":
                    try:
                        s.put_r(source, target)
                    except Exception as e:
                        s.put(source, target)
                    logging.critical("Uploaded from " + source + " to " + target)
                else:
                    logging.critical("Action of " + i + " is incorrect. Can only be up/down")
                    mailMessage += "Action of " + i + " is incorrect. Can only be up/down"
                exWrite = open("exclusion.txt", "a")
                exWrite.write("%s\r\n" % i)
                exWrite.close()
                s.close()
            else:

                mailMessage += i + " has already been run.\n"

                logging.critical(i + " has already been run")

        except Exception as e:
            logging.critical(e)
            mailMessage += str(e)
            print(e)
            return mailMessage

    return mailMessage


message = sftpDl(message)

try:
    server.sendmail(mailUser + "@gmail.com", mailUser + "@gmail.com", message)
except Exception as e:
    logging.critical(e)
    print(e)

logging.critical("Runtime: " + str(time.time() - startTime) + " seconds\n")
