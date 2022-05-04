import os
import re
import requests
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_bolt import App, Say
from slack_bolt.adapter.flask import SlackRequestHandler
from gcpstartvm import *
from gcpstopvm import *
from gcplistvms import *
from gcplistbuckets import *
from gcphighcpu import *
import json
import requests
from tabulate import tabulate

app = Flask(__name__)

METADATA_URL = 'http://metadata.google.internal/computeMetadata/v1/'
METADATA_HEADERS = {'Metadata-Flavor': 'Google'}
SERVICE_ACCOUNT = 'default'

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
bolt_app = App(token=os.environ.get("SLACK_BOT_TOKEN"),
signing_secret=os.environ.get("SLACK_SIGNING_SECRET"))

def get_access_token():
    url = '{}instance/service-accounts/{}/token'.format(
        METADATA_URL, SERVICE_ACCOUNT)
    # Request an access token from the metadata server.
    r = requests.get(url, headers=METADATA_HEADERS)
    r.raise_for_status()
    # Extract the access token from the response.
    access_token = r.json()['access_token']
    return access_token

'''/help command'''
@bolt_app.command("/help")
def help_command(payload: dict, say, ack):
    ack()
    access_token = get_access_token()
    help_command = ["/list-vms <project-id>" , "/start-vm <project-id> <zone> <instance-id>","/stop-vm <project-id> <zone> <instance-id>","/list-buckets <project-id>"]
    help_command_description = ["Lists all VMs in the specified project" , "Starts VM in the specified project and zone", "Stops VM in the specified project and zone", "Lists all buckets in the specified project"]
    output = ""
    length = len(help_command)
    for i in range(0,length):
        print(len(help_command[i]))
        output = output + "*" + help_command[i] + "* : " + help_command_description[i] + "\n"
    print(output)
    text = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Listing all commands"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": output
                }
            }
        ]
    }
    say(text=text)


@bolt_app.message(re.compile("(hi|hello|hey) gcp-booster"))
def greetings(payload: dict, say: Say):
    """ This will check all the message and pass only those which has 'hello slacky' in it """
    user = payload.get("user")
    say(f"Hi <@{user}>")

'''/list-vms command'''
@bolt_app.command("/list-vms")
def list_vms_command(payload: dict, say, ack):
    ack()
    project_id = payload.get("text")
    vms = list_vms(project_id)
    text = {
	"blocks": [
	    {
    		"type": "header",
    		"text": {
        	    "type": "plain_text",
    		    "text": "Listing VMs for project slack-app-346822"
    		}
    	    },
    	    {
    		"type": "divider"
    	    },
    	    {
    		"type": "section",
    		"text": {
    		    "type": "mrkdwn",
    		    "text": vms
    		}
    	    }
	]
    }
    say(text=text)

'''/start-vm command'''
@bolt_app.command("/start-vm")
def start_vms_command(payload: dict, say, ack):
    ack()
    access_token = get_access_token()
    param = payload.get("text")
    param = param.split()
    project_id = param[0]
    zone = param[1]
    instance = param[2]
    #print(project_id +" " + zone + " " + instance)
    status = start_vms(project_id, zone, instance)
    #status = "hello"
    text = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "OPERATION       STATUS"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": status
                }
            }
        ]
    }
    say(text=text)

'''/stop-vm command'''
@bolt_app.command("/stop-vm")
def stop_vms_command(payload: dict, say, ack):
    ack()
    access_token = get_access_token()
    param = payload.get("text")
    param = param.split()
    project_id = param[0]
    zone = param[1]
    instance = param[2]
    #print(project_id +" " + zone + " " + instance)
    status = stop_vms(project_id, zone, instance)
    #status = "hello"
    text = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "OPERATION       STATUS"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": status
                }
            }
        ]
    }
    say(text=text)


'''/list-buckets command'''
@bolt_app.command("/list-buckets")
def list_buckets_command(payload: dict, say, ack):
    ack()
    access_token = get_access_token()
    project_id = payload.get("text")
    buckets = list_buckets(access_token,project_id)
    text = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Listing Buckets for project slack-app-346822"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": buckets
                }
            }
        ]
    }
    say(text=text)

handler = SlackRequestHandler(bolt_app)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    """ Declaring the route where slack will post a request and dispatch method of App """
    return handler.handle(request)

'''API enpoint to receive alert if CPU exceeds threshold value. The alert is then sent to the Slack Webhook'''
@app.route('/highcpu', methods=['POST'])
def update_record_highcpu():
    record = json.loads(request.data)
    summary = record["incident"]["summary"]
    webhook = "https://hooks.slack.com/services/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"
    url = record["incident"]["url"]
    threshold = record["incident"]["threshold_value"]
    observed_value = record["incident"]["observed_value"]
    vm = record["incident"]["resource_display_name"]
    project = record["incident"]["scoping_project_id"]
    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "High CPU utilization Alert",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*<" + url + "|CPU utilization is above the threshold of " + threshold + " with a value of " + observed_value + ">* \n\n *VM*: " + vm + "\n *Project*: " + project
                }
            }
        ]
    }
    print(payload)
    send_slack_message(payload, webhook)
    code="success"
    return code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8469, debug=True)
