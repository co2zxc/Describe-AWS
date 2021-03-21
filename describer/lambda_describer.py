from describer import db_helpers as hp
import pandas as pd

#TODO: currently only showing up to 50
def describe():
    #client = boto3.client('lambda')
    client = hp.getBotoClient('lambda')
    functions = client.list_functions()['Functions']
    names, runtimes, handlers, memories, timeouts, vpcs, envs = [],[],[],[],[],[],[]
    for function in functions:
        name = hp.getFromJSON(function, 'FunctionName')
        runtime = hp.getFromJSON(function,'Runtime')
        handler = hp.getFromJSON(function,'Handler')
        memory = hp.getFromJSON(function, 'MemorySize')
        timeout = hp.getFromJSON(function, 'Timeout')
        vpc = hp.getFromJSON(hp.getFromJSON(function, 'VpcConfig'), 'VpcId')
        env = hp.getFromJSON(hp.getFromJSON(function, 'Environment'), 'Variables')
        names.append(name)
        runtimes.append(runtime)
        handlers.append(handler)
        memories.append(memory)
        timeouts.append(timeout)
        vpcs.append(vpc)
        envs.append(str(env))

    df = pd.DataFrame({"Function Name": names, "Runtime": runtimes, "Handler": handlers,"Timeout(s)": timeouts, "Memory(MB)": memories, "VPC": vpcs, "Environment Variables": envs})
    return df