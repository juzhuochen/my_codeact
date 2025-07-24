import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
import cloudpss
import time
import threading
def fetch(id,**kwargs):
    query = '''query ($input:JobInput!){
        job(input:$input){
            output
            context
        }
    }'''
    variables = {
        'input': {
            "id":id
            
        }
    }
    r = cloudpss.utils.graphql_request(query, variables)
    if 'errors' in r:
        raise Exception(r['errors'])
    job = r['data']['job']
    runner = cloudpss.Runner(id,job['output'], '', {"rid":job['context'][0].replace(
                                    'function/CloudPSS/','job-definition/cloudpss/')}, {}, '', {},
                    {}, **kwargs)

    event = threading.Event()
    thread = threading.Thread(target=runner._Runner__listen, kwargs=kwargs)
    thread.setDaemon(True)
    thread.start()

    while not runner._Runner__listenStatus():
        time.sleep(0.1)
    pass
    return runner


def fetchAllJob(status=None,limit=10,**kwargs):
    query = '''
    query ($input: JobsInput!) {
        jobs(input: $input) {
            items {
                id
                status
                context
            }
            count
            total
            cursor
        }
    }
    '''
    s=None
    if status is not None:
        s= ["or",status]
    variables = {
        "input": {
            "orderBy": [
                "createTime<"
            ],
            "cursor": [],
            "limit": limit,
            "status": s
        }
    }
    r = cloudpss.utils.graphql_request(query, variables)
    if 'errors' in r:
        raise Exception(r['errors'])
    return r['data']['jobs']['items']
    
    
def abort(id: str):
    query='''
        mutation ($input: AbortJobInput!){
            abortJob(input: $input) {
                id
            }
        }
    '''    
    

    variables = {
    "input": {
        "id": id,
        "timeout": 10
        }
    }
    r = cloudpss.utils.graphql_request(query, variables)
    return r

