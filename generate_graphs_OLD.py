import os
import random
import scipy
import matplotlib.pyplot as plt
import numpy as np
import glob
import pdb


def get_data(team_alias):
    pathname = "csvs/%s/times_results.csv" % (team_alias)
    times, results = np.loadtxt(pathname, delimiter=",",unpack=True)
    return times, results


def generate_histogram(team_alias):
    fig = plt.figure()      
    times, results  = get_data(team_alias)
    plt.hist(times, bins=8*10, range=(0,8), facecolor='green')
    plt.xlabel("Time to cross halfcourt (s)")
    plt.ylabel("Normalized frequency")
    plt.title("Histogram of time to cross halfcourt for %s" % (team_alias))
    fig.savefig("csvs/%s/tchc_histogram.png" % (team_alias))

def generate_barchart(team_alias):
    fig = plt.figure()      
    times, results = get_data(team_alias)
    hist, bins= np.histogram(times, bins=8*10,range=(0.00, 8.00), weights=results)
    hist1, bins1= np.histogram(times, bins=8*10, range=(0.00, 8.00))
    hist1 = np.array(map(lambda x: 1.0 if abs(x) == 0 else float(x), hist1))
    final_hist = hist/hist1
    bar_x = bins[:-1]
    plt.bar(left=bar_x, height=final_hist, width=0.1)
    plt.xlabel("Time to cross halfcourt (s)")
    plt.ylabel("Normalized points")
    plt.title("Points vs time to cross halfcourt for %s" % (team_alias))
    fig.savefig("csvs/%s/tchc_vs_results.png" % (team_alias))



if __name__ == "__main__":
    #times = []
    #for i in xrange(1000):
    #    times.append(random.uniform(0,8))
    folders = glob.glob("./csvs/*")
    teams = [folder.split("/")[-1] for folder in folders]
    for team_alias in teams:
        print "Generating graphs for %s \n" % (team_alias)
        generate_histogram(team_alias)
        generate_barchart(team_alias)


        


