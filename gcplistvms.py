import googleapiclient.discovery

compute = googleapiclient.discovery.build( "compute", "v1" )
project = "slack-app-346822"
zone = "us-west1-b"

def list_instances( compute, project):
    result = compute.instances().aggregatedList(project=project).execute()
    return result["items"] if "items" in result else None

def list_vms(project):
    temp = list_instances( compute, project)
    temp = temp["zones/us-west1-b"]
    temp = temp["instances"]
    length=len(temp)
    output = ""
    c=40
    for t in temp:
        name = t["name"].strip()
        status = t["status"].strip()
        zone = t["zone"].rsplit('/', 1)[1].strip()
        output = output + name + (' ' * (c-len(name))) + status + (' ' * (c-len(status))) + zone + "\n"
        #c = c-1
    return output

