#! /usr/bin/python3

"""
Utility script to simply get an entry from a json output from sophomorix and pretty print if it's a dictionary.
Make an alias like :

function soph {
        /PATH/TO/REPO/usr/lib/linuxmuster-webui/etc/SophomorixJsonOutput.py -c $1 -j $2
}

and then :

soph "sophomorix-query --student --schoolbase default-school --user-basic -jj" 'USER'
or
soph "['sophomorix-query', '--student', '--schoolbase', 'default-school', '--user-basic', '-jj']" 'USER'
or 
soph "sophomorix-query --student --schoolbase default-school --user-basic -jj" '*'
for complete dict.
"""

import threading
import ast
import json
import dpath.util
import subprocess
import re
import sys
import getopt
import time

class SophomorixProcess(threading.Thread):
    """Worker for processing sophomorix commands"""

    def __init__(self, command):
        self.stdout = None
        self.stderr = None
        self.command = command
        threading.Thread.__init__(self)

    def run(self):
        p = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        self.stdout, self.stderr = p.communicate()

def lmn_getSophomorixValue(sophomorixCommand, jsonpath, ignoreErrors=False):
    """Get the response dict or value for a key after running a sophomorix command"""

    ## New Thread for one process to avoid conflicts
    t = SophomorixProcess(sophomorixCommand)
    t.daemon = True
    t.start()
    t.join()

    ## Cleanup stderr output
    output = t.stderr.decode('utf-8').replace("null", "\"null\"")

    ## Some comands get many dicts, we just want the first
    output = output.replace('\n', '').split('# JSON-end')[0]
    output = re.sub('# JSON-begin', '', output)

    ## Convert str to dict
    jsonDict = {}
    if output:
        jsonDict = ast.literal_eval(output)

    # Option to only list keys on all levels
    keys = False
    if len(jsonpath)>=1 and jsonpath[-1] == '-':
        jsonpath = jsonpath[:-1]
        keys = True

    ## Without key, simply return the dict
    if jsonpath == '':
        if not keys:
            return jsonDict
        return list(jsonDict.keys())

    if ignoreErrors is False:
        try:
            resultDict = dpath.util.get(jsonDict, jsonpath)
        except Exception as e:
            raise Exception('getSophomorix Value error. Either sophomorix field does not exist or ajenti binduser does not have sufficient permissions:\n' +
                            'Error Message: ' + str(e) + '\n Dictionary we looked for information:\n' + str(jsonDict))
    else:
        resultDict = dpath.util.get(jsonDict, jsonpath)
    if not keys:
        return resultDict
    return sorted(list(resultDict.keys()))

def main(argv):
    jsonpath = ''
    try:
        opts, _ = getopt.getopt(argv,"hc:j:",["command=","jsonpath="])
    except getopt.GetoptError:
        print('Get a JSON entry from a sophomorix output.')
        print('Soph.py -c <SophomorixCommand> -j <JSONPATH>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Get a JSON entry from a sophomorix output.')
            print('Soph.py -c <SophomorixCommand> -j <JSONPATH>')
            sys.exit()
        elif opt in ("-c", "--command"):
            command = arg
            if command[0] == "[" and command[-1] == "]":
                print("OK, working directly with a list.")
                sophomorixCommand = ast.literal_eval(command)
            elif isinstance(command, str):
                print("OK, working with a complete command, splitting up.")
                sophomorixCommand = command.split()
            else:
                print("Type not supported. Exiting")
                sys.exit(2)
        elif opt in ("-j", "--jsonpath"):
            if arg != "*":
                jsonpath = arg
    if len(opts) >= 1:
        result = lmn_getSophomorixValue(sophomorixCommand, jsonpath)
        if isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(result)
    
if __name__ == "__main__":
    start = time.time()
    main(sys.argv[1:])
    end = time.time()
    duration = end - start
    print(f"Duration : {duration:.3f}")
