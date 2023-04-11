import pandas as pd

from dash.dash_table import DataTable, FormatTemplate
from dash.dash_table.Format import Format, Padding, Scheme

percentage = FormatTemplate.percentage(4)

DEBUG_LOG = False

def statistics_in_each_segment(df, alg_1: str, alg_2: str, x_column: str, y_column: str, mtx_column: str, alg_column: str, segments: [int]):
    df1 = pd.DataFrame(columns=['alg1', 'alg2', 'xstart', 'xend', 'max_speedup', 'min_speedup', 'mean_speedup', 'beat_count', 'total_count', 'beat_ratio'])
    seg_num = len(segments)
    for i in range(seg_num - 1):
        range_start = segments[i]
        range_end = segments[i + 1]
        df1.loc[len(df1)] = log_anslysis(df.copy(), alg_1, alg_2, x_column, y_column, mtx_column, alg_column, range_start, range_end)
    if DEBUG_LOG:
        print(df1)
    # column in table
    columns = [
        dict(id='alg1', name='Algorithm 1'),
        dict(id='alg2', name='Algorithm 2'),
        dict(id='xstart', name='X Start'),
        dict(id='xend', name='X End (not include)'),
        dict(id='max_speedup', name='Max Speedup', type='numeric', format=Format(precision=4, scheme=Scheme.fixed)),
        dict(id='min_speedup', name='Min Speedup', type='numeric', format=Format(precision=4, scheme=Scheme.fixed)),
        dict(id='mean_speedup', name='Mean speedup', type='numeric', format=Format(precision=4, scheme=Scheme.fixed)),
        dict(id='beat_count', name='Beat count'),
        dict(id='total_count', name='Total Count'),
        dict(id='beat_ratio', name='Beat Ratio', type='numeric', format=percentage),
    ]

    return df1, columns

# anslysis the speedup cases of 2 algorithm.
# note: for range, it does not include range_end.
def log_anslysis(csr_data, alg_a: str, alg_b: str, x_column: str, y_column: str, mtx_column: str, alg_column: str, range_start: int, range_end: int):
    our_data = csr_data[csr_data[alg_column] == alg_a]
    other_data = csr_data[csr_data[alg_column] == alg_b]

    merged_data = pd.merge(our_data, other_data, how='inner', on=mtx_column) # inner join
    # merged_data.drop(merged_data[(merged_data.failed_count_x > 0) | (merged_data.failed_count_y > 0)].index, inplace=True)
    sort_merged_data = merged_data.sort_values(by=x_column + '_x')

    df = sort_merged_data[(sort_merged_data[x_column + '_x'] >= range_start) & (sort_merged_data[x_column + '_x'] < range_end)].copy()
    df['speedup'] = df[y_column+'_x'] / df[y_column+'_y']

    # find max,min and mean.
    better_df = df[df.speedup >= 1.0]
    beat_ratio = 0 if len(df.index) == 0 else len(better_df.index) / len(df.index)
    return [alg_a, alg_b, range_start, range_end,
        df['speedup'].max(), df['speedup'].min(), df['speedup'].mean(),
        len(better_df.index), len(df.index), beat_ratio]
