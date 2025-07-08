#!/bin/bash

sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip
sudo apt install rabbitmq-server


#generate the private and pub keys 
sudo mkdir -p /etc/dkim
sudo openssl genrsa -out /etc/dkim/private.key 2048
sudo openssl rsa -in /etc/dkim/private.key -pubout -out /etc/dkim/public.key
sudo chmod 600 /etc/dkim/private.key

#create working dir
mkdir -p /opt/smtp-server
cd /opt/smtp-server
git clone "https://github.com/allanz998/dekrinsmtp.git"
mv dekrinsmtp/* .
cd TempmailBot 


clear
echo "Attention:"
echo "======================================----=="

echo "Add a TXT record with name: mail._domainkey.yourdomain.com"
echo "Value: v=DKIM1; k=rsa; p=[PUBLIC_KEY_CONTENT]"
echo ""
echo "Copy this and add use as the PUBLIC_KEY_CONTENT. Dont include the headers and footers"
echo "======================================----=="
cat /etc/dkim/public.key
echo ""
sudo ufw allow 25/tcp   # SMTP
sudo ufw allow 587/tcp  # Submission (i will use this to send out emails when implemented)


#now the rest is about launching the stuff
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

nohup python3 manage.py bot & nohup python3 manage.py smtp
