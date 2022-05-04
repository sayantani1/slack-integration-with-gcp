from pprint import pprint

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

credentials = GoogleCredentials.get_application_default()

service = discovery.build('compute', 'v1', credentials=credentials)

def start_vms(project, zone, instance):
    # Project ID for this request.
    #project = 'slack-app-346822'  

    # The name of the zone for this request.
    #zone = 'us-west1-b' 

    # Name of the instance resource to start.
    #instance = 'instance-1'  

    request = service.instances().start(project=project, zone=zone, instance=instance)
    response = request.execute()
    status ="Start VM                    " + response["status"]
    return status

    # TODO: Change code below to process the `response` dict:
    #pprint(response)
