import subprocess
import os
import json

maps = ["../maps/maps4_4_p30.map","../maps/maps8_8_p50.map"]

def run_simple(robot_path, map_path):
    cmd = "python ../main.py -c --simulation_time_limit=1000 -r {0} -m {1}".format(robot_path, map_path)
    print "Running ",cmd
    x = subprocess.Popen(cmd,
                         stdout=subprocess.PIPE, shell=True)
    output = x.communicate()[0]
    return output.splitlines()[-1]

def test_simple(robot_path):
    results = []
    for m in maps:
        results.append(json.loads(run_simple(robot_path,m)))
    return results

if __name__ == "__main__":
    print test_simple("../examples/turner.py")