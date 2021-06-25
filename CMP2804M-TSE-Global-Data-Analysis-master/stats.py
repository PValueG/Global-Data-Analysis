import pandas as pd
import numpy as np
from sklearn.preprocessing import PowerTransformer


def normalize(df, norm_type):
    if norm_type == 'Min-Max':
        df_num = df.select_dtypes(include=[np.number])
        df_num = df_num.apply(lambda x: (x - np.mean(x)) / (np.max(x) - np.min(x)))
        df[df_num.columns] = df_num
    elif norm_type == 'Z-Score':
        df_num = df.select_dtypes(include=[np.number])
        df_num = df_num.apply(lambda x: (x - np.mean(x)) / np.std(x))
        df[df_num.columns] = df_num
    return df


def power_transform(df):
    df_num = df.select_dtypes(include=[np.number])
    transformer = PowerTransformer(standardize = False)
    df_num = pd.DataFrame(transformer.fit_transform(df_num), columns = df_num.columns)
    df[df_num.columns] = df_num
    return df
