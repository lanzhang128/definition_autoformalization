import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    datasets = ['minif2f', 'wiki', 'arxiv']
    metrics = ['Success', 'SYN', 'UDF', 'TUF']
    scores = {ds: pd.read_csv(f'ref_{ds}.csv', index_col=0) for ds in datasets}

    # setup
    colors = {
        'ZS': '#f5b2b0',
        '(ZS)+Binary': '#e2827c',
        '(ZS)+Detailed': '#cc5b55',
        # 'ZS+SYN': '#b7e3b1',
        # 'ZS+UDF': '#a8cbe6',
        # 'ZS+TUF': '#d5b3db',
        '(ZS)+CR-SYN': '#83c888',
        '(ZS)+CR-UDF': '#6ea8d6',
        '(ZS)+CR-TUF': '#b890c5',
        '(ZS)+Detailed+CR-SYN': '#4e9a5d',
        '(ZS)+Detailed+CR-UDF': '#357abd',
        '(ZS)+Detailed+CR-TUF': '#9b6aad'
    }
    models = list(colors.keys())
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 50
    x = np.arange(len(datasets))
    width = 1 / (len(models) + 3)
    offset = - (len(models) - 1) * width / 2

    # individual
    ylims = [(120, 20), (60, 10), (75, 15), (25, 5)]
    for i in range(len(metrics)):
        ms = metrics[i]
        values = np.vstack([scores[ds].loc[ms][models] for ds in datasets])
        if ms == 'Success':
            values = 100 - values
        fig, ax = plt.subplots(figsize=(24, 15), constrained_layout=True)
        for j in range(len(models)):
            loc = x + offset + j * width
            rects = ax.bar(loc, values[:, j], width, label=models[j], color=colors[models[j]])

        ax.legend(markerscale=1.0, loc='upper right', ncols=3, fontsize=44)
        ax.set_xticks(x, ['MiniF2F Test', 'Def_Wiki Test', 'Def_ArXiv'], fontsize=60)
        ax.grid(axis='y', linestyle='--')
        ax.set_ylabel(f'Percentage (%)', fontsize=60)
        ax.set_yticks(range(0, ylims[i][0]+1, ylims[i][1]))
        plt.savefig(f'ref_{ms}.pdf')
        plt.close()

    # combined
    ylims = [(100, 10), (60, 10), (60, 10), (20, 5)]
    fig, ax = plt.subplots(figsize=(45, 25), nrows=2, ncols=2)
    for i in range(len(metrics)):
        ms = metrics[i]
        values = np.vstack([scores[ds].loc[ms][models] for ds in datasets])
        if ms == 'Success':
            values = 100 - values
        for j in range(len(models)):
            loc = x + offset + j * width
            rects = ax[i // 2][i % 2].bar(loc, values[:, j], width, label=models[j], color=colors[models[j]])

        ax[i // 2][i % 2].set_title(f'{ms} Error Rate')
        ax[i // 2][i % 2].grid(axis='y', linestyle='--')
        ax[i // 2][i % 2].set_yticks(range(0, ylims[i][0] + 1, ylims[i][1]))

    ax[0][0].set_ylabel(f'Percentage (%)')
    ax[0][1].legend(markerscale=1.0, loc='upper right', ncols=3)
    ax[1][0].set_ylabel(f'Percentage (%)')
    ax[0][0].set_xticks([])
    ax[0][1].set_xticks([])
    ax[1][0].set_xticks(x, ['MiniF2F Test', 'Def_Wiki Test', 'Def_ArXiv'])
    ax[1][1].set_xticks(x, ['MiniF2F Test', 'Def_Wiki Test', 'Def_ArXiv'])
    plt.tight_layout(pad=0.0)
    plt.savefig(f'ref.pdf')
    plt.close()
