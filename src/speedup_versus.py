#!/usr/bin/env python3

import plotly.graph_objects as go
import plotly.io as pio   

import pandas as pd
# pio.kaleido.scope.mathjax = None


# keys_csr_mtx = 'csr_mtx'
# keys_nnz = 'nnz'
# keys_flops = 'GFLOPS(total_time)'
# keys_hover_data = ['nnz/row', 'mid calc cost', 'mid total cost']

def gen_plot_speedup(csr_data, alg1_name, alg2_name, keys_csr_mtx, keys_nnz, keys_flops):
    our_data = csr_data[csr_data.strategy == alg1_name]
    other_data = csr_data[csr_data.strategy == alg2_name]

    merged_data = pd.merge(our_data, other_data, how='inner', on=keys_csr_mtx) # inner join
    sort_merged_data = merged_data.sort_values(by=keys_nnz + '_x')

    # get nnz, flat flops, hola flops.
    nnzs = sort_merged_data[keys_nnz + '_x'].tolist()
    a_flops = sort_merged_data[keys_flops+'_x'].tolist() # flops of our method
    b_flops = sort_merged_data[keys_flops+'_y'].tolist() # flops of other method to be compared.

    # calculate speedup
    speedup_a = []
    speedup_b = []
    base_line = []

    N = len(a_flops)
    for i in range(N):
        speedup = a_flops[i]/b_flops[i]
        base_line.append(1.0)
        if(speedup == 0.0): # no adaptive data
            speedup_a.append(1.0)
            speedup_b.append(1.0)
        else:
            if(speedup > 1.0):
                speedup_a.append(speedup)
                speedup_b.append(1.0)
            else:
                speedup_b.append(speedup)
                speedup_a.append(1.0)


    fig = go.Figure([
        go.Scatter(
            x=nnzs + nnzs[::-1], # nnz, then nnz reversed
            y=speedup_a + speedup_b[::-1], # speedup_a, then base_line reversed
            fill='toself',
            fillcolor='rgba(0,100,80, 0.75)',
            # line=dict(color='rgba(0,100,80,0.6)'),
            hoverinfo="skip",
            # showlegend=False,
            mode='none',
            name='Our Adaptive',
        ),
    ])

    fig.update_xaxes(type="log")
    fig.update_yaxes(type="log")
    fig.update_layout(
        xaxis_title="NNZ",
        yaxis_title="Speedup",
        xaxis_nticks=20,
        yaxis_nticks=12,
        yaxis_tick0=1,
        xaxis_tick0=0.1,
        xaxis_tickangle=0,
        xaxis_ticks="inside",
        yaxis_ticks="inside",
        xaxis_gridwidth=0.5,
        yaxis_gridwidth=0.5,
        width=1200,
        height=800,
        legend_title="Algorithms",
        font=dict(
            family="Times New Roman, monospace",
            size=18,
            color="RebeccaPurple"
        )
    )

    return fig
