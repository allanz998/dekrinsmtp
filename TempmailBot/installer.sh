#!/bin/bash

sudo apt update && sudo apt upgrade -y
python3 -m ensurepip --upgrade
sudo apt install python3-pip
sudo apt install python3-venv
sudo apt install rabbitmq-server



#generate the private and pub keys 
sudo mkdir -p /etc/dkim
sudo openssl genrsa -out /etc/dkim/private.key 2048
sudo openssl rsa -in /etc/dkim/private.key -pubout -out /etc/dkim/public.key
sudo chmod 600 /etc/dkim/private.key

#create working dir
sudo rm -rf /opt/smtp-server
sudo rm -rf /etc/systemd/system/bot.service
sudo rm -rf /etc/systemd/system/smtp-server.service
sudo systemctl disable bot
sudo systemctl disable smtp-server

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
pip install -r ./requirements.txt

#nohup python3 manage.py bot & nohup python3 manage.py smtp

#Bot Service
cat << EOF > /etc/systemd/system/bot.service
    [Unit]
    Description=Temporary Mail system by Olwa Inventions
    After=network.target

    [Service]
    User=root
    Type=simple
    ExecStart=/opt/smtp-server/TempmailBot/venv/bin/python3 /opt/smtp-server/TempmailBot/manage.py bot 
    WorkingDirectory=/opt/smtp-server/TempmailBot
    Restart=always

    [Install]
    WantedBy=multi-user.target
EOF

sudo chmod 640 /etc/systemd/system/bot.service
sudo systemctl daemon-reload
sudo systemctl enable bot
sudo systemctl start bot
echo "Bot Dispatch: $(systemctl is-active bot)"


#SMTP Service


cat << EOF > /etc/systemd/system/smtp-server.service
    [Unit]
    Description=SMTP Server logic by Olwa Inventions
    After=network.target

    [Service]
    User=root
    Type=simple
    ExecStart=/opt/smtp-server/TempmailBot/venv/bin/python3 /opt/smtp-server/TempmailBot/manage.py smtp
    WorkingDirectory=/opt/smtp-server/TempmailBot
    Restart=always

    [Install]
    WantedBy=multi-user.target
EOF

sudo chmod 640 /etc/systemd/system/smtp-server.service
sudo systemctl daemon-reload
sudo systemctl enable smtp-server
sudo systemctl start smtp-server
echo "SMTP SERVER: $(systemctl is-active smtp-server)"
