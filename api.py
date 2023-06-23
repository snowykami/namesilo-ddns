import email
import json
import os
import time
import traceback
from typing import List
import requests
import xmltodict
import smtplib
from email.mime.text import MIMEText
from models import DNSRecord
import socket

config = json.load(open("config.json", "r", encoding="utf-8"))


class Account:

    def __init__(self, key: str = ""):
        self.key = key

    def set_key(self, key: str):
        self.key = key

    def list_dns_records(self, domain: str) -> List[DNSRecord]:
        url = "https://www.namesilo.com/api/dnsListRecords?"
        params = {
            "version": "1",
            "type": "xml",
            "key": self.key,
            "domain": domain
        }

        resp = requests.get(url=url, params=params)
        return [DNSRecord(**record) for record in xmltodict.parse(resp.text)["namesilo"]["reply"]["resource_record"]]

    def add_dns_record(self, domain: str, rrtype: str, rrhost: str, rrvalue: str, rrdistance: str = "10",
                       rrttl: str = "3600") -> bool:
        """
        :param rrdistance:
        :param domain: The domain associated with the DNS resource record to modify
        :param rrtype: A|AAAA|CNAME|MX|TXT
        :param rrhost: The hostname to use (there is no need to include the ".DOMAIN")
        :param rrvalue: The value for the resource record
        :param rrttl: The TTL for this record (default is 7207 if not provided)
        :return:
        """
        url = "https://www.namesilo.com/api/dnsAddRecord?"
        params = {
            "version": "1",
            "type": "xml",
            "key": self.key,
            "domain": domain,
            "rrtype": rrtype,
            "rrhost": rrhost,
            "rrvalue": rrvalue,
            "rrttl": rrttl,
            "rrdistance": rrdistance
        }
        if rrtype == "MX":
            params["rrdistance"] = "10"
        resp = requests.get(url=url, params=params)
        r = xmltodict.parse(resp.text)["namesilo"]["reply"]["detail"] == "success"
        if r:
            send_email("域名解析添加成功", f"{rrhost}.{domain} -> {rrvalue}")
        else:
            send_email("域名解析添加失败", f"{json.dumps(xmltodict.parse(resp.text))}")
        return r

    def update_dns_record(self, domain: str, rrid: str, rrhost: str, rrvalue: str, rrdistance: str = "10",
                          rrttl: str = "3600") -> bool:
        """
        :param rrdistance: Only used for MX (default is 10 if not provided)
        :param rrid: The unique ID of the resource record. You can get this value using dnsListRecords.
        :param domain: The domain associated with the DNS resource record to modify
        :param rrhost: The hostname to use (there is no need to include the ".DOMAIN")
        :param rrvalue: The value for the resource record
        :param rrttl: The TTL for this record (default is 7207 if not provided)
        :return:
        """
        url = "https://www.namesilo.com/api/dnsUpdateRecord?"
        params = {
            "version": "1",
            "type": "xml",
            "key": self.key,
            "domain": domain,
            "rrid": rrid,
            "rrhost": rrhost,
            "rrvalue": rrvalue,
            "rrttl": rrttl,
            "rrdistance": rrdistance
        }

        resp = requests.get(url=url, params=params)
        r = xmltodict.parse(resp.text)["namesilo"]["reply"]["detail"] == "success"
        if r:
            send_email("域名解析更新成功", f"{rrhost}.{domain} -> {rrvalue}")
        else:
            send_email("域名解析更新失败", f"{json.dumps(xmltodict.parse(resp.text))}")
        return r

    def delete_dns_record(self, domain: str, rrid: str):
        """
        :param domain:
        :param rrid:
        :return:
        """
        url = "https://www.namesilo.com/api/dnsDeleteRecord?"
        params = {
            "version": "1",
            "type": "xml",
            "key": self.key,
            "domain": domain,
            "rrid": rrid
        }
        resp = requests.get(url=url, params=params)
        return True if xmltodict.parse(resp.text)["namesilo"]["reply"]["detail"] == "success" else False


class logger:

    @staticmethod
    def get_time():
        return "{0:0>4d}-{1:0>2d}-{2:0>2d} {3:0>2d}:{4:0>2d}:{5:0>2d}".format(*list(time.localtime()))

    @staticmethod
    def info(text):
        print(f"{logger.get_time()} [INFO] {text}")

    @staticmethod
    def success(text):
        print(f"{logger.get_time()} \033[92m[SUCCESS]\033[0m {text}")

    @staticmethod
    def error(text):
        print(f"{logger.get_time()} \033[91m[ERROR]\033[0m {text}")


def send_email(title: str, content: str):
    """
    :param title:
    :param content:
    :return:

    发送邮箱验证码,请在此前校验邮箱格式
    """
    try:
        if len(config["receivers"]) >= 1:
            mail_host = config.get("mail_host")
            mail_user = config.get("mail_user")
            mail_auth = config.get("mail_auth")
            mail_port = config.get("mail_port")

            sender = config.get("sender")

            receivers = config.get("receivers")

            if mail_host is None:
                raise BaseException

            try:
                email = open("email/notification.html", "r", encoding="utf-8").read()
                email = email.replace("#time#", logger.get_time())
                email = email.replace("#title#", title)
                email = email.replace("#content#", content)
                email = email.replace("#device#", socket.gethostname())
            except:
                pass

            message = MIMEText(email, "html", "utf-8")
            message["Subject"] = title
            message["From"] = sender
            message["To"] = ",".join(receivers)
            try:
                smtpObj = smtplib.SMTP(mail_host, mail_port)
                smtpObj.connect(mail_host, mail_port)
                smtpObj.ehlo()
                smtpObj.starttls()
                smtpObj.login(mail_user, mail_auth)
                smtpObj.sendmail(sender, receivers, msg=message.as_string())
                return True
            except smtplib.SMTPException as e:
                traceback.print_exc()
                return False
    except:
        pass


def get_current_ipv4() -> str:
    return requests.get('https://v4.ident.me').text


def get_current_ipv6() -> str:
    return requests.get('https://v6.ident.me').text
