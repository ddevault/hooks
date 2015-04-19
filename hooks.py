from flask import Flask, request, abort
from configparser import ConfigParser

import sys
import os
from subprocess import Popen, PIPE, STDOUT
import urllib
import json
import logging

config_paths = ["./config.ini", "/etc/hooks.conf"]
config = ConfigParser()
for p in config_paths:
    try:
        config.readfp(open(p))
        break
    except:
        pass

app = Flask(__name__)

class Hook():
    def __init__(self, name, config):
        self.name = name
        self.repository = config.get(name, "repository")
        self.branch = config.get(name, "branch")
        self.command = config.get(name, "command")
        self.valid_ips = config.get(name, "valid_ips")

hooks = list()

for key in config:
    if key == 'DEFAULT':
        continue
    hooks.append(Hook(key, config))

print("Loaded {} hooks".format(len(hooks)))

def makeMask(n):
    return (2 << n - 1) - 1

def dottedQuadToNum(ip):
    parts = ip.split(".")
    return int(parts[0]) | (int(parts[1]) << 8) | (int(parts[2]) << 16) | (int(parts[3]) << 24)

def networkMask(ip, bits):
    return dottedQuadToNum(ip) & makeMask(bits)

def addressInNetwork(ip, net):
    return ip & net == net

@app.route('/hook', methods=['POST'])
def hook_publish():
    raw = request.data.decode("utf-8")
    try:
        event = json.loads(raw)
    except:
        return "Hook rejected: invalid JSON", 400
    repository = "{}/{}".format(event["repository"]["owner"]["name"], event["repository"]["name"])
    matches = [h for h in hooks if h.repository == repository]
    if len(matches) == 0:
        return "Hook rejected: unknown repository {}".format(repository)
    hook = matches[0]

    allow = False
    remote = request.remote_addr
    if remote == "127.0.0.1" and "X-Real-IP" in request.headers:
        remote = request.headers.get("X-Real-IP")
    for ip in hook.valid_ips.split(","):
        parts = ip.split("/")
        range = 32
        if len(parts) != 1:
            range = int(parts[1])
        addr = networkMask(parts[0], range)
        if addressInNetwork(dottedQuadToNum(remote), addr):
            allow = True
    if not allow:
        return "Hook rejected: unauthorized IP", 403

    if any("[noupdate]" in c["message"] for c in event["commits"]):
        return "Hook ignored: commit specifies [noupdate]"

    if "refs/heads/" + hook.branch == event["ref"]:
        print("Executing hook for " + hook.name)
        p=Popen(hook.command.split(), stdin=PIPE)
        p.communicate(input=raw.encode())
        return "Hook accepted"

    return "Hook ignored: wrong branch"
