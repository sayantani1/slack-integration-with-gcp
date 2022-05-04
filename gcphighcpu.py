import json
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def send_slack_message(payload, webhook):
    """Send a Slack message to a channel via a webhook. 
    
    Args:
        payload (dict): Dictionary containing Slack message, i.e. {"text": "This is a test"}
        webhook (str): Full Slack webhook URL for your chosen channel. 
    
    Returns:
        HTTP response code, i.e. <Response [503]>
    """

    return requests.post(webhook, json.dumps(payload))

