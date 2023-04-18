#!/usr/bin/env python3

import plotly.graph_objects as go
import plotly.io as pio   

import pandas as pd
pio.kaleido.scope.mathjax = None

class PlotConfig:
    def __init__(self, plot_color, plot_font_color, plot_font_size, plot_xaxis_title, plot_yaxis_title, plot_showlegend,
    plot_legend_title, plot_width, plot_height):
        self.color = plot_color
        self.font_color = plot_font_color
        self.font_size = plot_font_size
        self.xaxis_title = plot_xaxis_title
        self.yaxis_title = plot_yaxis_title
        self.showlegend = plot_showlegend
        self.legend_title = plot_legend_title
        self.width = plot_width
        self.height = plot_height

# keys_csr_mtx = 'csr_mtx'
# keys_nnz = 'nnz'
# keys_flops = 'GFLOPS(total_time)'
# keys_hover_data = ['nnz/row', 'mid calc cost', 'mid total cost']

def gen_plot_speedup(csr_data, alg1_name, alg2_name, keys_csr_mtx, keys_nnz, keys_flops, alg_column: str, config: PlotConfig):
    our_data = csr_data[csr_data[alg_column] == alg1_name]
    other_data = csr_data[csr_data[alg_column] == alg2_name]

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
            fillcolor=config.color,
            # line=dict(color='rgba(0,100,80,0.6)'),
            hoverinfo="skip",
            showlegend=config.showlegend,
            mode='none',
            name='Our Adaptive',
        ),
    ])

    fig.update_xaxes(type="log")
    fig.update_yaxes(type="log")
    fig.update_layout(
        xaxis=dict(
            title=config.xaxis_title,
            tickangle=-45,
            ticks="inside",
            nticks=20,
            tick0=0.1,
            gridcolor="#e8e8e8",
            gridwidth=0.5,
        ),
        yaxis =dict(
            title=config.yaxis_title,
            ticks="inside",
            nticks=12,
            tick0=1,
            gridcolor="#e8e8e8",
            gridwidth=0.5,
        ),
        plot_bgcolor="rgb(255,255,255)",
        width=config.width,
        height=config.height,
        legend_title=config.legend_title,
        margin=dict(l=0, r=0, b=0, t=0),
        font=dict(
            family="Times New Roman, monospace",
            size=config.font_size,
            color=config.font_color
        )
    )

    fig.update_xaxes(showline = True, linecolor = 'black', linewidth = 1, mirror = True)
    fig.update_yaxes(showline = True, linecolor = 'black', linewidth = 1, mirror = True)

    return fig
