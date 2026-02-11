import pandas as pd
import numpy as np

def load_data(trans_path, acc_path):
    """
    Load transaction and account data from CSV files.
    """
    df_trans = pd.read_csv(trans_path)
    df_acc = pd.read_csv(acc_path)
    return df_trans, df_acc

def preprocess_features(df_trans, df_acc=None):
    """
    Apply feature engineering transformations to the transaction DataFrame.
    """
    # Renaming columns to standard names
    rename_map = {
        'Timestamp': 'timestamp',
        'Account': 'from_acc',
        'From Bank': 'from_bank',
        'To Bank': 'to_bank',
        'Account.1': 'to_acc',
        'Amount Received': 'amount',
        'Receiving Currency': 'curr',
        'Amount Paid': 'amount_paid',
        'Payment Currency': 'curr_paid',
        'Payment Format': 'payment_type',
        'Is Laundering': 'is_laundering',
    }
    # Check if we need to rename (in case it's already renamed or raw)
    # Using intersection to avoid errors if some columns are missing or already renamed
    cols_to_rename = {k: v for k, v in rename_map.items() if k in df_trans.columns}
    if cols_to_rename:
        df_trans.rename(columns=cols_to_rename, inplace=True)

    # Date and basic features
    # FIX: use pandas api for dtype check to handle StringDtype or object safely
    if not pd.api.types.is_datetime64_any_dtype(df_trans['timestamp']):
        df_trans['timestamp'] = pd.to_datetime(df_trans['timestamp'])
    
    df_trans['is_self_tx'] = (df_trans['from_acc'] == df_trans['to_acc']).astype(int)
    df_trans['is_cross_bank'] = (df_trans['from_bank'] != df_trans['to_bank']).astype(int)
    df_trans['hour'] = df_trans['timestamp'].dt.hour
    df_trans['log_amount'] = np.log1p(df_trans['amount'])
    df_trans['log_amount_paid'] = np.log1p(df_trans['amount_paid'])
    df_trans["cross_currency"] = (df_trans["curr"] != df_trans["curr_paid"]).astype(int)

    # Risk Map
    risk_map = {
        "Cash": "High",
        "Bitcoin": "High",
        "Wire": "Medium",
        "ACH": "Low",
        "Cheque": "Low",
        "Credit Card": "Low",
        "Reinvestment": "Low"
    }
    df_trans["payment_type_risk"] = df_trans["payment_type"].map(risk_map)

    # Graph/Interaction features
    
    # In-degree / Out-degree
    df_trans["in_degree"] = df_trans.groupby("to_acc")["from_acc"].transform("nunique")
    df_trans["out_degree"] = df_trans.groupby("from_acc")["to_acc"].transform("nunique")
    
    df_trans["stack_degree_flag"] = (
        (df_trans["in_degree"] == 1) &
        (df_trans["out_degree"] == 1)
    ).astype(int)
    
    # Sorting for time-based calculations
    df_trans = df_trans.sort_values("timestamp")
    
    df_trans["time_since_prev_tx"] = (
        df_trans
            .groupby("from_acc")["timestamp"]
            .diff()
            .dt.total_seconds() / 3600
    )
    
    df_trans["amount_ratio_prev"] = (
        df_trans
            .groupby("from_acc")["amount"]
            .transform(lambda x: x / x.shift(1))
            .replace([np.inf, -np.inf], np.nan)
    )
    
    df_trans["returns_to_origin"] = (
        df_trans["to_acc"].isin(df_trans["from_acc"])
    ).astype(int)
    
    df_trans["account_seen_before"] = (
        df_trans.groupby("from_acc").cumcount() > 0
    ).astype(int)
    
    df_trans["currency_change"] = (
        df_trans["curr"] !=
        df_trans.groupby("from_acc")["curr"].shift()
    ).astype(int)
    
    # Fan-in / Fan-out (Daily)
    # Using dt.date for daily grouping
    df_trans["fanin_degree"] = (
        df_trans
            .groupby(["to_acc", df_trans["timestamp"].dt.date])["from_acc"]
            .transform("nunique")
    )
    
    df_trans["fanin_amount_sum"] = (
        df_trans
            .groupby(["to_acc", df_trans["timestamp"].dt.date])["amount"]
            .transform("sum")
    )
    
    df_trans["fanin_flag"] = (df_trans["fanin_degree"] >= 3).astype(int)
    
    df_trans["fanout_degree"] = (
        df_trans
            .groupby(["from_acc", df_trans["timestamp"].dt.date])["to_acc"]
            .transform("nunique")
    )
    
    df_trans["gather_scatter_flag"] = (
        (df_trans["fanin_degree"] >= 3) &
        (df_trans["fanout_degree"] >= 3)
    ).astype(int)
    
    df_trans["same_payment_type_chain"] = (
        df_trans["payment_type"] ==
        df_trans.groupby("from_acc")["payment_type"].shift()
    ).astype(int)

    return df_trans
