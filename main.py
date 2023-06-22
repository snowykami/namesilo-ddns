import traceback
from threading import Thread
from api import *
import json
import time

key = config["key"]
host_ipv4 = config["host_ipv4"]
host_ipv6 = config["host_ipv6"]
duration = config.get("config", 600)
domain = config["domain"]

account = Account(key)
last_ipv4 = "0.0.0.0"
last_ipv6 = ":::::::"


def update():
    global last_ipv4, last_ipv6

    records = account.list_dns_records(domain)
    # detect local change
    current_ipv4 = get_current_ipv4()
    if current_ipv4 != last_ipv4:
        for record in records:
            # update new record
            if record.host == f"{host_ipv4}.{domain}" and record.type == "A":
                r = account.update_dns_record(domain=domain, rrid=record.record_id, rrhost=host_ipv4,
                                              rrvalue=current_ipv4)
                if r:
                    logger.success(f"Succeed to update: {host_ipv4}.{domain} -> {current_ipv4}")
                else:
                    logger.error(f"Failed to update: {host_ipv4}.{domain} -> {current_ipv4}")
                break
        else:
            # No ipv4 record, add new
            r = account.add_dns_record(domain=domain, rrtype="A", rrvalue=current_ipv4, rrhost=host_ipv4)
            if r:
                logger.success(f"Succeed to add: {host_ipv4}.{domain} -> {current_ipv4}")
            else:
                logger.error(f"Failed to add: {host_ipv4}.{domain} -> {current_ipv4}")
        if r:
            last_ipv4 = current_ipv4
    else:
        logger.info(f"IPv4 No change: {current_ipv4}")

    current_ipv6 = get_current_ipv6()
    if current_ipv6 != last_ipv6:

        for record in records:
            if record.host == f"{host_ipv6}.{domain}" and record.type == "AAAA":
                r = account.update_dns_record(domain=domain, rrid=record.record_id, rrhost=host_ipv6,
                                              rrvalue=current_ipv6)
                if r:
                    logger.success(f"Succeed to update: {host_ipv6}.{domain} -> {current_ipv6}")
                else:
                    logger.error(f"Failed to update record: {host_ipv6}.{domain} -> {current_ipv6}")
                break
        else:
            # No ipv4 record, add new
            r = account.add_dns_record(domain=domain, rrtype="AAAA", rrvalue=current_ipv6, rrhost=host_ipv6)
            if r:
                logger.success(f"Succeed to add: {host_ipv6}.{domain} -> {current_ipv6}")
            else:
                logger.error(f"Failed to add: {host_ipv6}.{domain} -> {current_ipv6}")
        if r:
            last_ipv6 = current_ipv6
    else:
        logger.info(f"IPv6 No change: {current_ipv6}")


logger.info("Start")
logger.info("Sending start email")
send_email("域名解析更新服务已启动", "启动成功")
while True:
    try:
        update()
        time.sleep(duration)
    except BaseException as e:
        traceback.print_exc()
