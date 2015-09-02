#!/usr/bin/env python
"""
Update IP for hover

Most code from https://gist.github.com/dankrause/5585907

usage:
    update.py --username=USERNAME --password=PASSWORD <domain> [--ip=IP] [-d]
    update.py --config=CONFIG <domain> [--ip=IP] [-d]

options:

    --username=USERNAME  Your username on hover.com
    --password=PASSWORD  Your password on hover.com
    <domain>             Domain to update (naked domain should be @.domail.com)
    --ip=IP              IP to set, if empty get external IP from icanhazip.com

    --config=CONFIG      Read usernameand password from a INI like file

    -d                   Enable debug messages
"""

import ConfigParser
import docopt
import requests
import sys
import logging

VERSION = "1.0.1"


class HoverException(Exception):
    pass


class HoverAPI(object):
    def __init__(self, username, password):
        params = {"username": username, "password": password}
        response = requests.post("https://www.hover.com/api/login", params=params)
        logging.debug(response)
        if not response.ok or "hoverauth" not in response.cookies:
            raise HoverException(response)
        self.cookies = response.cookies

    def call(self, method, resource, data=None):
        url = "https://www.hover.com/api/{0}".format(resource)
        response = requests.request(method, url, data=data, cookies=self.cookies)
        if not response.ok:
            raise HoverException(response)
        if response.content:
            body = response.json()
            if "succeeded" not in body or body["succeeded"] is not True:
                raise HoverException(body)
            return body


def get_public_ip():
    logging.info("Getting public IP")
    return requests.get("http://icanhazip.com").content


def update_dns(username, password, fqdn, the_ip):
    try:
        client = HoverAPI(username, password)
    except HoverException:
        raise HoverException("Authentication failed")
    dns = client.call("get", "dns")

    dns_id = None
    for domain in dns["domains"]:
        if fqdn == domain["domain_name"]:
            fqdn = "{domain_name}".format(domain_name=domain["domain_name"])
        logging.info("Looking for the domain to update")
        for entry in domain["entries"]:
            if entry["type"].upper() != "A":
                continue
            logging.debug("ENTRY: ")
            logging.debug(entry)
            logging.debug(entry["name"])
            logging.debug(domain["domain_name"])
            logging.debug(fqdn)
            if "{0}.{1}".format(entry["name"], domain["domain_name"]) == fqdn:
                dns_id = entry["id"]
                break
    if dns_id is None:
        logging.critical("No DNS record found for {0}".format(fqdn))
        raise HoverException("No DNS record found for {0}".format(fqdn))

    logging.info("Updating IP on Hover")
    response = client.call("put", "dns/{0}".format(dns_id), {"content": the_ip})

    if "succeeded" not in response or response["succeeded"] is not True:
        logging.exception(response)
        raise HoverException(response)

    logging.info("Updated record for {0} to: {1}".format(fqdn, the_ip))
    print "Updated record for {0} to: {1}".format(fqdn, the_ip)


def main(args):
    if args["--username"]:
        username, password = args["--username"], args["--password"]
    else:
        config = ConfigParser.ConfigParser()
        config.read(args["--config"])
        items = dict(config.items("hover"))
        username, password = items["username"], items["password"]

    domain = args["<domain>"]
    the_ip = args.get("--ip")
    if not the_ip:
        the_ip = get_public_ip()
    logging.debug(the_ip)

    try:
        logging.debug(username, password, domain, the_ip)
        update_dns(username, password, domain, the_ip)
    except HoverException as exception:
        print "Unable to update DNS: {0}".format(exception)
        return 1

    return 0


if __name__ == "__main__":
    ARGS = docopt.docopt(__doc__, version=VERSION)
    THE_LEVEL = logging.INFO
    if ARGS["-d"]:
        THE_LEVEL = logging.DEBUG

    try:
        import coloredlogs
        coloredlogs.install(level=THE_LEVEL)
    except ImportError:
        logging.basicConfig(level=THE_LEVEL)

    logging.debug(ARGS)
    STATUS = main(ARGS)
    sys.exit(STATUS)
