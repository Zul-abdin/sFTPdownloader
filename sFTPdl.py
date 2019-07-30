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
        toDownload = True
        remotepath = doc["connInfo"][i]["remotepath"]
        localpath = doc["connInfo"][i]["localpath"]
        hostname = doc["connInfo"][i]["hostname"]
        username = doc["connInfo"][i]["username"]
        password = doc["connInfo"][i]["password"]

        try:
            exRead = open("exclusion.txt", "r")
            f1 = exRead.readlines()
            for x in f1:
                if x == (i + "\n"):
                    toDownload = False
                    break
            exRead.close()

            if toDownload:
                s = sftp.Connection(host=hostname, username=username, password=password, cnopts=cnopts)
                s.get(remotepath, localpath)

                exWrite = open("exclusion.txt", "a")
                exWrite.write("%s\r\n" % i)
                exWrite.close()
                logging.critical("Downloaded from " + i)
                s.close()
            else:
                server.login(mailUser, mailPass)

                mailMessage += i + " has already been downloaded.\n"

                logging.critical(i + " has already been downloaded")

        except Exception as e:
            logging.critical(e)
            mailMessage += e
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
