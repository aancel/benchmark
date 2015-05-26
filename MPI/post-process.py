#!/usr/bin/python

import os
import shutil
import matplotlib
import matplotlib.pyplot as plt

# method generating graphs from data output from IMB
def generateGraphs(infile):

    f = open(infile, "r")

    # make the directory where the graphs will be stored
    dpath = infile + "_fig"
    if(os.path.exists(dpath)):
        shutil.rmtree(dpath)
    os.makedirs(dpath)

    benchmarkName = ""
    processorCount = 0
    readingBenchmark = False
    benchmarkContent = ""
    lines = f.readlines()
    # iterate over output lines and extract relevant data
    for line in lines:
        s = line.lstrip()
        if(s.find("# Benchmarking") == 0):
            l = s.split()
            if( l[2] != benchmarkName ):
                benchmarkName = l[2]
                print("Adding new benchmark " + l[2])
        if(s.find("#processes") != -1):
            l = s.split()
            processorCount = int(l[3])
        # Start reading the current benchmark
        if(s.find("#bytes") != -1 or s.find("#repetitions") != -1):
            readingBenchmark = True
            print("Start reading benchmark")
        # Mark the end of reading a benchmark
        if(s.find("#----") == 0 and readingBenchmark == True):
            readingBenchmark = False
            print("End reading benchmark")

            # Extrct the data from the benchmark
            labels=[]
            results=[]
            nEntries = -1
            benchmarkLines = benchmarkContent.split("\n")
            for benchmarkLine in benchmarkLines:
                l = benchmarkLine.split()
                if(nEntries == -1):
                    nEntries = len(l)
                    for i in range(nEntries):
                        results.append([])
                        labels.append(l[i])
                else:
                    if(len(l) == nEntries):
                        for i in range(nEntries):
                            results[i].append(l[i])
            # Build the plot
            #for i in range(nEntries - 1):
            #    plt.plot(results[0], results[i+1])
            plt.title(os.path.basename(infile) + ": " + benchmarkName + "_" + str(processorCount))
            matplotlib.rc('xtick', labelsize=10)
            matplotlib.rc('ytick', labelsize=10)
            plt.xlabel(labels[0])
            plt.ylabel(labels[nEntries - 1])
            plt.plot(results[0], results[nEntries - 1])
            #plt.show()
            plt.savefig(dpath + "/" + benchmarkName + "_" + str(processorCount) + ".png", format="png")

            benchmarkContent = ""

        # if we are reading a benchmark we store the associated data
        if(readingBenchmark):
            benchmarkContent = benchmarkContent + s

def main():
    # change dir to the latest benchmark
    os.chdir("benchmark-latest")

    # list all the files in this directory
    # get the list of .out files
    # generate graphs for each of them
    for fname in os.listdir("."):
        root, ext = os.path.splitext(fname)
        print root + " " + ext
        if(ext == ".out"):
            generateGraphs(fname)

main()
