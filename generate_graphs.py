import os
import random
import scipy
import matplotlib.pyplot as plt
import numpy as np
import glob
import pdb
from scipy.stats.stats import pearsonr
from scipy.stats.stats import spearmanr 

def get_data(team_alias):
    pathname = "csvs/%s/times_results.csv" % (team_alias)
    times, results = np.loadtxt(pathname, delimiter=",",unpack=True)
    return times, results

def aggregate_data():
    folders = glob.glob("./csvs/*")
    folders = filter(lambda folder: not ("aggregate" in folder), folders)
    agg_dir = "csvs/aggregate/"
    if os.path.isdir(agg_dir) == False:
        os.mkdir(agg_dir, 0777)
    agg_csv = open(agg_dir+"times_results.csv", 'w')
    for folder in folders:
        if 'aggregate' in folder:
            continue
        team_csv = open(folder+"/times_results.csv",'r')
        content = team_csv.read()
        agg_csv.write(content)


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
    pdb.set_trace()
    hist1 = np.array(map(lambda x: 1.0 if abs(x) == 0 else float(x), hist1))
    final_hist = hist/hist1
    bar_x = bins[:-1]
    plt.scatter(bar_x, final_hist)
    # plt.bar(left=bar_x, height=final_hist, width=0.1)
    plt.xlabel("Time to cross halfcourt (s)")
    plt.ylabel("Average points per possession")
    plt.title("Avg points vs time to cross halfcourt for %s" % (team_alias))
    fig.savefig("csvs/%s/tchc_vs_results.png" % (team_alias))

def generate_graphs(team_alias):
    fig = plt.figure(figsize=(15,6))
    ax = fig.add_subplot(121)
    times_to_cross, results  = get_data(team_alias)
    ax.hist(times_to_cross, bins=8*10, range=(0,8), facecolor='green')
    plt.xlabel("Time to cross halfcourt (s)")
    plt.ylabel("Normalized frequency")
    plt.title("Histogram of time to cross halfcourt for %s" % (team_alias))
    mean = np.mean(times_to_cross)
    std = np.std(times_to_cross)
    n = len(times_to_cross)

    text = ax.text(0.05, 0.85,'Mean: {:.2f} \nStd Dev: {:.2f} \n# Possessions: {: d}'.format(mean,std,n),transform = ax.transAxes)


    ax2 = fig.add_subplot(122)
    points, times= np.histogram(times_to_cross, bins=8*10,range=(0.00, 8.00), weights=results)
    num_crosses, times= np.histogram(times_to_cross, bins=8*10, range=(0.00, 8.00))
    to_remove = []
    for index, ncross in enumerate(num_crosses):
        if abs(ncross) == 0:
            to_remove.append(index)

    points = np.delete(points, to_remove)
    num_crosses = np.delete(num_crosses, to_remove)
    times = np.delete(times, to_remove)
    # hist1 = np.array(map(lambda x: 1.0 if abs(x) == 0 else float(x), hist1))
    avg_points = points/num_crosses
    times = np.delete(times, -1)
    ax2.scatter(times, avg_points)
    #avg = np.mean(avg_points)
    #std = np.std(avg_points)
    #corr, pvals = pearsonr(times, avg_points)
    #ax2.text(0.05,0.85, 'Avg: {:.2f} \nStd Dev: {:.2f} \nPearson\' corr: {:.2f}'.format(avg, std, corr), transform=ax2.transAxes)

    avg_all = np.mean(avg_points)
    std = np.std(avg_points)
    pcorr_all, p_val = pearsonr(times_to_cross, results)
    spcorr_all, sp_val = spearmanr(times_to_cross, results)
    ax2.text(0.05,0.85, 'Pearson Corr: {:.2f}\n\
            Pearson 2t_val: {:.2f}\n\
            Spearman Corr: {:.2f}\n\
            Spearman 2t_val: {:.2f}'.format(pcorr_all, p_val, spcorr_all, sp_val), transform=ax2.transAxes)

    # plt.bar(left=bar_x, height=final_hist, width=0.1)
    plt.xlabel("Time to cross halfcourt (s)")
    plt.ylabel("Average points per possession")
    plt.title("Avg points vs time to cross halfcourt for %s" % (team_alias))
    fig.savefig("csvs/%s/graphs.png" % (team_alias))
    # plt.show()
    # pdb.set_trace()



if __name__ == "__main__":
    #times = []
    #for i in xrange(1000):
    #    times.append(random.uniform(0,8))
    aggregate_data()
    folders = glob.glob("./csvs/*")
    teams = [folder.split("/")[-1] for folder in folders]
    for team_alias in teams:
        print "Generating graphs for %s \n" % (team_alias)
        generate_graphs(team_alias)


        


