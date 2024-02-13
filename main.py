import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json
import logging
import sys
from datetime import datetime
import smtplib
import email.message


class Browser:
    browser, service = None, None

    # Initialise the webdriver with the path to chromedriver.exe
    def __init__(self, driver: str):
        self.service = Service(driver)
        self.browser = webdriver.Chrome(service=self.service)
        self.browser.set_page_load_timeout(14400)

    def open_page(self, url: str):
        self.browser.get(url)
        self.browser.delete_all_cookies()

    def close_browser(self):
        self.browser.close()

    def add_input(self, by: By, value: str, text: str):
        field = self.browser.find_element(by=by, value=value)
        field.send_keys(text)
        time.sleep(1)

    def click_button(self, by: By, value: str):
        button = self.browser.find_element(by=by, value=value)
        button.click()
        time.sleep(1)

    def login_stacks(self, clientcode: str, username: str, password: str):
        self.add_input(by=By.ID, value='ClientModel_ClientCode', text=clientcode)
        self.add_input(by=By.ID, value='textInput1', text=username)
        self.add_input(by=By.ID, value='textInput2', text=password)
        self.click_button(by=By.ID, value='btnLogin')

    def get_url(self):
        url = self.browser.current_url
        logger.debug("The current url is : "+str(url))
        print("The current url is : "+str(url))
        return str(url)



if __name__ == '__main__':
    try:
        # Create and configure logger
        current_datetime = datetime.now()
        current_date_time = current_datetime.strftime("%m_%d_%Y")
        
        Filename="Logs\\Logs_{}.log".format(current_date_time)
        logging.basicConfig(filename=Filename,
                            format='%(asctime)s %(message)s',
                            filemode='a')
        
        # Creating an object
        logger = logging.getLogger()

        # Setting the threshold of logger to DEBUG
        logger.setLevel(logging.DEBUG)

        # Setting the threshold of logger to DEBUG

        
        with open("params.json") as jsonFile:
            jsonObject = json.load(jsonFile)
            jsonFile.close()
            email_from = jsonObject['fromemail']
            email_to = jsonObject['toemail']
            email_cc = jsonObject['ccemail']
            email_bcc = jsonObject['bccemail']
            smtp_user = jsonObject['smtpuser']
            email_password = jsonObject['password']
            client = jsonObject['client'].split(",")
            user = jsonObject['user'].split(",")
            pwd = jsonObject['pwd'].split(",")
            loginpage = jsonObject['loginpage'].split(",")
            nextpage = jsonObject['nextpage'].split(",")

        env = "Production"

        
        for i in range(len(client)):
            
            email_content = """
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            #customers {
            font-family: Arial, Helvetica, sans-serif;
            border-collapse: collapse;
            width: 100%;
            }

            #customers td, #customers th {
            border: 1px solid #ddd;
            padding: 8px;
            }

            #customers tr:nth-child(even){background-color: #f2f2f2;}

            #customers tr:hover {background-color: #ddd;}

            #customers th {
            padding-top: 12px;
            padding-bottom: 12px;
            text-align: left;
            background-color: #04AA6D;
            color: white;
            }
            </style>
            </head>
            <body>

            <h1>Login Report</h1>

            <table id="customers">
            <tr>
                <th>Client</th>
                <th>User</th>
                <th>Status</th>
                <th>Login Time Required in Hrs:min:sec:msec</th>
            </tr>
            """
            browser = Browser('drivers/chromedriver')

            browser.open_page(loginpage[i])
            time.sleep(3)
            logger.debug("\n----------------------------------------------- {} Client Login Started -----------------------------------------------\n".format(client[i]))

            startlogin_datetime = datetime.now()

            browser.login_stacks(clientcode=client[i], username=user[i], password=pwd[i])
            endlogin_datetime = datetime.now()
            
            tdelta = endlogin_datetime - startlogin_datetime
            print(tdelta)

            print("Time required : {}".format(tdelta))
            get_url = browser.get_url()
            if(get_url==nextpage[i]):
                logger.debug("{} Login Success...!!! on {} for Client {}".format(user[i],env,client[i]))
                print("{} Login Success...!!! on {} for client {}".format(user[i],env,client[i]))
                row="""
                <tr>
                    <td>{}</td>
                    <td>{}</td>
                    <td>Login Successful</td>
                    <td>{}</td>
                </tr>
                """.format(client[i],user[i],tdelta)
                email_content="".join((email_content, row))
            else :
                logger.debug("{} Login failed on {} for client {} wrong credentials...!!!".format(user[i],env,client[i]))
                print("{} Login failed on {} for client {} wrong credentials...!!!".format(user[i],env,client[i]))
                row="""
                <tr>
                    <td>{}</td>
                    <td>{}</td>
                    <td>Login Failed</td>
                    <td>{}</td>
                </tr>
                """.format(client[i],user[i],tdelta)
                email_content="".join((email_content, row))
            time.sleep(5)
            browser.close_browser()
           
            # Sending email
            end="""</table>

            </body>
            </html>
            """
            email_content="".join((email_content, end))
            message_subject = 'Login Status Report for client {}'.format(client[i])
            
            
            rcpt = email_cc.split(",") + email_bcc.split(",") + [email_to]
            s = smtplib.SMTP('smtp.gmail.com',587)
            msg = email.message.Message()
            msg['Subject'] = message_subject
            msg['From'] = email_from
            msg['To'] = email_to
            msg['Cc'] = email_cc
            msg['Bcc'] = email_bcc
            password = email_password
            msg.add_header('Content-Type', 'text/html')

            msg.set_payload(email_content)
            s.starttls()

            # Login Credentials for sending the mail 
            s.login(smtp_user, password)

            s.sendmail(msg['From'], rcpt, msg.as_string())
            s.quit()
            
            logger.debug("\n----------------------------------------------- {} Client Login END -----------------------------------------------\n".format(client[i]))
        

    except Exception as e:
        
        logger.debug("Login failed...!!! with error "+e)
        print("Login failed...!!! with error "+e)

        email_content="""
        <!DOCTYPE html>
        <html>
        <body>

        <h1>Login Report</h1>

        <h2>Stacks 1.0 Auto Login Script Execution Failed</h2>
        <h3 style="color:red">Error Occured : {}</h4>

        </body>
        </html>
        """.format(e)

        rcpt = email_cc.split(",") + email_bcc.split(",") + [email_to]

        s = smtplib.SMTP('smtp.gmail.com',587)
        msg = email.message.Message()
        msg['Subject'] = 'Login Status Report'
        msg['From'] = email_from
        msg['To'] = email_to
        msg['Cc'] = email_cc
        msg['Bcc'] = email_bcc
        password = email_password
        msg.add_header('Content-Type', 'text/html')

        msg.set_payload(email_content)
        s.starttls()

        # Login Credentials for sending the mail 
        s.login(smtp_user, password)

        s.sendmail(msg['From'], rcpt, msg.as_string())
        s.quit()

        browser.close_browser()
    
    logger.debug("\n\n------------------------------------------------------XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX------------------------------------------------------\n\n")
