import pandas as pd

# TODO: mouse list to pandas -> refine_data.list_to_pandas
def mouse_list_to_pandas(d_list):
    df = pd.DataFrame(d_list, columns=["x",
                                       'y',
                                       "type",
                                       'timestamp'])
    return df