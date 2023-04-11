#!/usr/bin/env python3

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio   

import pandas as pd
pio.kaleido.scope.mathjax = None

from speedup_versus import *


def gen_plot_performance(csr_data, keys_csr_mtx, keys_strategy, keys_nnz, keys_flops, algs_select: [str], config: PlotConfig):
    keys_hover_data = ['nnz/row', 'mid calc cost', 'mid total cost']
    tab = csr_data[csr_data[keys_strategy].isin(algs_select)]

    fig = px.scatter(tab,
        x=keys_nnz,
        y=keys_flops,
        # error_y="y_error",
        log_x=True,
        # log_y=True,
        color=keys_strategy,
        symbol=keys_strategy,
        hover_name=keys_csr_mtx,
        hover_data=keys_hover_data,
        # range_x=[10000, 1000000],
        # range_y=[0, 40],
        # trendline="rolling",
        # trendline_options=dict(function="median", window=5),
        # trendline_options=dict(window=10),
        # trendline="expanding",
        ).update_traces(marker_size=3) # "lines+markers"

    # fig.update_traces(marker_size=1)

    # fig.update_traces(error_y_thickness=0.5) # update error bar style

    # remove pointes
    # fig.data = [t for t in fig.data if t.mode == "lines"] #trendlines have showlegend=False by default
    fig.update_traces(showlegend=config.showlegend) 

    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    fig.update_xaxes(showline = True, linecolor = 'black', linewidth = 1, row = 1, col = 1, mirror = True)
    fig.update_yaxes(showline = True, linecolor = 'black', linewidth = 1, row = 1, col = 1, mirror = True)

    fig.update_layout(
         xaxis=dict(
            title=config.xaxis_title,
            gridcolor="#e8e8e8",
            gridwidth=0.5,
            # dtick=1,
            ticks="outside",
            nticks=20,
            tick0=0.1,
            tickangle=0,
        ),
        yaxis =dict(
            title=config.yaxis_title,
            ticks="outside",
            gridcolor="#e8e8e8",
            gridwidth=0.5,
            nticks=12,
            tick0=1,
            # dtick=1,
            # range=[1, 5000],
            # exponentformat="power",
            # tickmode="array",
            # showline=False,
            # ticks="inside",
        ),
        plot_bgcolor="rgb(255,255,255)",
        margin=dict(l=0, r=0,b=0,t=0),
        width=config.width,
        height=config.height,
        legend_title=config.legend_title,
        font=dict(
            family="Times New Roman, monospace",
            size=config.font_size,
            color=config.font_color,
        )
    )

    return fig
