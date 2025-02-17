import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


if __name__ == '__main__':
    # setup
    dataset = ['minif2f', 'wiki', 'arxiv']
    variants = ['base', 'SR', 'Post-FDG', 'Post-FDG+SR']
    colors = ['#b7e3b1', '#a8cbe6', '#d5b3db', '#4e9a5d', '#357abd', '#9b6aad']
    scores = {
        'minif2f': {
            'zs': [
                [25.41, -6.15, -23.77, -7.38],
                [25.41, -6.15, -23.77, -7.38],
                [67.21, -3.28, -2.87, -5.33],
                [67.21, -3.28, -2.87, -5.33]],
            'zs_det': [
                [37.30, -5.74, -9.02, -8.61],
                [37.30, -5.74, -9.02, -8.61],
                [83.61, -2.05, -0.82, -3.28],
                [83.61, -2.05, -0.82, -3.28]]
        },
        'wiki': {
            'zs': [
                [10.87, -19.57, -50.00, -13.04],
                [10.87, -15.22, -52.17, -13.04],
                [34.78, -30.43, -17.39, -23.91],
                [34.78, -23.91, -19.57, -28.26]],
            'zs_det': [
                [19.57, -10.87, -47.83, -10.87],
                [19.57, -8.70, -47.83, -10.87],
                [43.48, -21.74, -10.87, -23.91],
                [43.48, -17.39, -10.87, -28.26]]
        },
        'arxiv': {
            'zs': [
                [13.33, -40.00, -56.66, -6.67],
                [13.33, -23.33, -66.67, -6.67],
                [23.33, -60.00, -13.33, -13.33],
                [23.33, -60.00, -13.33, -13.33]],
            'zs_det': [
                [16.67, -36.67, -43.33, -16.67],
                [16.67, -23.33, -46.67, -20.00],
                [30.00, -56.67, -13.33, -3.33],
                [30.00, -56.67, -13.33, -3.33]]
        }
    }

    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 50
    x = np.arange(4)
    width = 1 / 6
    offset = - width
    # individual
    ylims = [(-10, 60, 10), (-20, 50, 10), (-30, 60, 10)]
    for i in range(len(dataset)):
        for m in ['zs', 'zs_det']:
            fig, ax = plt.subplots(figsize=(16, 12), constrained_layout=True)
            score = scores[dataset[i]][m]
            for j in range(1, len(variants)):
                loc = x + offset + (j - 1) * width
                diff = np.array(score[j]) - np.array(score[0])
                rects = ax.bar(loc, diff, width, label=variants[j], color=colors[j-1])

            ax.legend(markerscale=1.0, loc='upper right', ncols=3, fontsize=40)
            ax.set_xticks(x, ['Overall', 'SYN', 'UDF', 'TUF'], fontsize=60)
            ax.grid(axis='y', linestyle='--')
            ax.set_ylabel(f'Gain (%)', fontsize=60)
            ax.set_yticks(range(ylims[i][0], ylims[i][1]+1, ylims[i][2]))
            plt.savefig(f'fdg_{dataset[i]}_{m}.pdf')
            plt.close()
