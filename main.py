import traceback
from threading import Thread
from api import *
import json
import time

key = config["key"]
host_ipv4 = config["host_ipv4"]
host_ipv6 = config["host_ipv6"]
duration = config.get("duration", 1200)
domain = config["domain"]

logger.info("Starting service...")
account = Account(key)


def update():

    last_ipv4, last_ipv6 = "", ""
    rrid_ipv4, rrid_ipv6 = None, None
    dns_records = account.list_dns_records(domain)

    # Detect cloud records
    for dns_record in dns_records:
        if dns_record.type == 'A' and dns_record.host == host_ipv4:
            last_ipv4 = dns_record.value
            rrid_ipv4 = dns_record.record_id
        if dns_record.type == 'AAAA' and dns_record.host == host_ipv6:
            last_ipv6 = dns_record.value
            rrid_ipv6 = dns_record.record_id

    # Detect local change
    current_ipv4 = get_current_ipv4()
    current_ipv6 = get_current_ipv6()
    if last_ipv4 != current_ipv4:
        if rrid_ipv4 is not None:
            r = account.update_dns_record(domain, rrid_ipv4, host_ipv4, current_ipv4)
            if r:
                logger.info(f"Update record: {host_ipv4}.{domain} -> {current_ipv4}")
            else:
                logger.error(f"Failed to update record: {host_ipv4}.{domain} -> {current_ipv4}")
        else:
            r = account.add_dns_record(domain, "A", host_ipv4, current_ipv4)
            if r:
                logger.info(f"Add record: {host_ipv4}.{domain} -> {current_ipv4}")
            else:
                logger.info(f"Failed to add record: {host_ipv4}.{domain} -> {current_ipv4}")
    else:
        logger.info(f"IPv4 no change: {current_ipv4}")
    if last_ipv6 != current_ipv6:
        if rrid_ipv6 is not None:
            r = account.update_dns_record(domain, rrid_ipv6, host_ipv6, current_ipv6)
            if r:
                logger.info(f"Update record: {host_ipv6}.{domain} -> {current_ipv6}")
            else:
                logger.info(f"Failed to update record: {host_ipv6}.{domain} -> {current_ipv6}")
        else:
            r = account.add_dns_record(domain, "AAAA", host_ipv6, current_ipv6)
            if r:
                logger.info(f"Add record: {host_ipv6}.{domain} -> {current_ipv6}")
            else:
                logger.info(f"Failed to add record: {host_ipv6}.{domain} -> {current_ipv6}")
    else:
        logger.info(f"IPv6 no change: {current_ipv6}")


while True:
    try:
        update()
        time.sleep(duration)
    except BaseException as e:
        traceback.print_exc()
