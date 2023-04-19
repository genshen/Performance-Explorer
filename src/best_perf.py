import pandas as pd

from dash.dash_table import DataTable, FormatTemplate
from dash.dash_table.Format import Format, Padding, Scheme

percentage = FormatTemplate.percentage(4)

DEBUG_LOG = False


def statistics_best_perf_in_each_segment(df, x_column: str, y_column: str, mtx_column: str, alg_column: str, selected_algs: [str], segments: [int], drop_rows_by_col_value: str):
    df1 = pd.DataFrame(columns=['algo', 'xstart', 'xend', 'best_count', 'total_count', 'best_ratio'])
    seg_num = len(segments)
    for i in range(seg_num - 1):
        range_start = segments[i]
        range_end = segments[i + 1]
        best_record = find_best(df, x_column, y_column, mtx_column, alg_column, selected_algs, drop_rows_by_col_value, range_start, range_end)
        if DEBUG_LOG:
            print_best(best_record)
        # save the results of the best.
        best_grouped = best_record.groupby("best_algorithm")
        for name, group in best_grouped:
            df1.loc[len(df1)] = [name, range_start, range_end, len(group), len(best_record), len(group) / len(best_record),]
    if DEBUG_LOG:
        print(df1)
    # column in table
    columns = [
        dict(id='algo', name='Algorithms'),
        dict(id='xstart', name='X Start'),
        dict(id='xend', name='X End (not include)'),
        dict(id='best_count', name='Best count'),
        dict(id='total_count', name='Total Count'),
        dict(id='best_ratio', name='Best Ratio', type='numeric', format=percentage),
    ]

    return df1, columns

# find best search the pandas.
# Find the max performance of each matrix and record the matrix name, algorithm name and performance value.
def find_best(csr_data, keys_nnz, keys_flops, keys_csr_mtx, keys_strategy, selected_strategies, drop_rows_by_col_value, range_start, range_end):
    # select nnz first
    csr_data = csr_data[(csr_data[keys_nnz] >= range_start) & (csr_data[keys_nnz] < range_end)]
    # ignore cases when verification failed
    if drop_rows_by_col_value != None:
        csr_data.drop(csr_data[(csr_data[drop_rows_by_col_value] > 0)].index, inplace=True) # todo:
    # select strategies
    df = csr_data[csr_data[keys_strategy].isin(selected_strategies)]
    grouped = df.groupby(keys_csr_mtx) # group by matrix name

    print("avaiabled groups:", len(grouped))
    best_records = pd.DataFrame(columns=[keys_csr_mtx, 'best_flops', 'best_algorithm'])
    should_discard = 0
    for name, group in grouped:
        if len(group) != len(selected_strategies):
            should_discard = should_discard + 1
            # continue # still keep the incompleted group
        _id = group[keys_flops].idxmax()
        best = group.loc[_id]
        best_records.loc[len(best_records)] = [best[keys_csr_mtx], best[keys_flops], best[keys_strategy]]
        # break
    print("should discarded(incompleted) groups:", should_discard)
    return best_records

def print_best(df):
    best_grouped = df.groupby("best_algorithm")
    best_counter = pd.DataFrame(columns=["strategy", "cases_number_of_best"])
    for name, group in best_grouped:
        best_counter.loc[len(best_counter)] = [name, len(group)]
    print(best_counter)
