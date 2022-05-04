import os
import re
import requests
from flask import Flask, request
from slack_sdk import WebClient
from slack_bolt import App, Say
from slack_bolt.adapter.flask import SlackRequestHandler

def list_buckets(access_token,project_id):
    url = 'https://www.googleapis.com/storage/v1/b'
    params = {
        'project': project_id
    }
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    length = len(r.json()["items"])
    output = ""
    for i in range(length):
        temp = r.json()["items"][i]
        name = temp["name"]
        location = temp["location"]
        storageClass = temp["storageClass"]
        output = output + name + (' ' * (40-len(name))) + location + (' ' * (40-len(location))) + storageClass + "\n"
    return output
