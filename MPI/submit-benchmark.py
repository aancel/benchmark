#!/usr/bin/python

import os
import datetime
import sys
import time
import subprocess

#benchmarks = ["IMB-MPI1", "IMB-EXT", "IMB-IO", "IMB-NBC", "IMB-RMA"]
benchmarks = ["IMB-MPI1", "IMB-EXT", "IMB-IO", "IMB-NBC", "IMB-RMA"]

# execute a command line
def executeCommand(text, cmd, useShell=True, debug=0):
    out = ""
    ret = 0

    print text

    tstart = time.time()

    if(debug > 0):
        print cmd

    # if we specify an absolute command path
    # we check that the file exists
    if(os.path.isabs(cmd[0])):
        if(not os.path.exists(cmd[0])):
            return 1, ""

    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=useShell)
    except subprocess.CalledProcessError, e:
        out = e.output
        ret = e.returncode

    tend = time.time()

    t = (tend - tstart)

    if(debug > 0):
        print "Time spent: " + str(t)

    if(ret == 0):
        print "OK"
    else:
        print "FAILED"

    return ret, out, t

def main():

    # create a benchmark directory with current time
    now = datetime.datetime.now()

    benchmarkPath = "benchmark_" + now.isoformat()
    os.makedirs(benchmarkPath)
    print("Writing benchmarks in " + benchmarkPath)

    if(os.path.exists("benchmark-latest")):
        os.remove("benchmark-latest")
    os.symlink(benchmarkPath, "benchmark-latest")
    os.chdir(benchmarkPath)

    bl = False

    # create the slum scripts
    for b in benchmarks:
        for it in ["tcp", "ib"]:
            benchmarkName = "slurm-" + b + "-" + it
            f = open(benchmarkName + ".sh", "w")
            f.write("#!/bin/bash\n")
            f.write("#SBATCH -p public\n")
            f.write("#SBATCH -n 96\n")
            f.write("#SBATCH -o " + benchmarkName + ".out\n")
            print(sys.argv)
            if(len(sys.argv) == 2):
                f.write("#SBATCH --mail-type=END\n")
                f.write("#SBATCH --mail-user=" + sys.argv[1] + "\n")

            # output slurm job id
            f.write("echo \"SLURM_JOB_ID=${SLURM_JOB_ID}\"\n")

            f.write("source /etc/profile.d/modules.sh\n")

            f.write("PREVPATH=`pwd`\n")
            f.write("cd /data/software/config/etc\n")
            f.write("source feelpprc.sh\n")
            f.write("cd ${PREVPATH}\n")
            f.write("module load gcc490.profile\n")

            f.write("cd /data/software/src/benchmark/imb/src\n")
            if(it == "tcp"):
                f.write("mpirun -mca btl tcp,self --bind-to-core ./" + b + "\n")
            elif(it == "ib"):
                f.write("mpirun --bind-to-core ./" + b + "\n")

            f.close()

            executeCommand("Submitting " + benchmarkName + ".sh", "sbatch " + benchmarkName + ".sh")

main()
