import argparse
import pandas as pd
import sys
import os

# Add the project root to python path to allow imports if run from inside src or root
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.features import load_data, preprocess_features


def main():
    parser = argparse.ArgumentParser(description="AML Pipeline")
    parser.add_argument("--trans", type=str, default="data/LI-Small_Trans.csv", help="Transactions CSV path")
    parser.add_argument("--acc", type=str, default="data/LI-Small_accounts.csv", help="Accounts CSV path")
    parser.add_argument("--n_iter", type=int, default=10, help="Number of optimization iterations")
    parser.add_argument("--model", type=str, default="all", help="Model to train (all, lightgbm, decision_tree, svc)")
    
    args = parser.parse_args()
    
    # ... (existing checks)

    # ... (feature engineering)

    if not os.path.exists(args.trans):
        print(f"Error: Transaction file not found at {args.trans}")
        return
    if not os.path.exists(args.acc):
        print(f"Error: Account file not found at {args.acc}")
        return

    print(f"Loading data from {args.trans} and {args.acc}...")
    df_trans, df_acc = load_data(args.trans, args.acc)
    
    print("Preprocessing features...")
    df_processed = preprocess_features(df_trans, df_acc)
    
    print(f"Processed dataframe shape: {df_processed.shape}")
    
    # Prepare X and y
    target_col = "is_laundering"
    if target_col not in df_processed.columns:
        print(f"Error: Target column '{target_col}' not found in processed data.")
        print("Columns available:", df_processed.columns.tolist())
        return
        
    y = df_processed[target_col]
    X = df_processed.drop(columns=[target_col])
    
    # Drop columns that are not predictive or leak info
    # 'timestamp' is used for feature engineering but probably shouldn't be a raw feature
    if 'timestamp' in X.columns:
        X = X.drop(columns=['timestamp'])
        
    # Drop ID columns usually shouldn't be features unless high cardinality handling is good
    # For now, keeping logical approach of removing them if they are high cardinality strings
    # But let's rely on mlapp pipeline which has 'infer_columns' and 'rare_categories' 
    # However, unique IDs like 'from_acc' (if practically unique per row mostly) are bad.
    # The notebook didn't explicitly drop them in feature engineering cell, but might have later (I didn't see all cells).
    # I'll drop them to be safe.
    drop_cols = ['from_acc', 'to_acc', 'from_bank', 'to_bank', 'payment_type'] # payment_type mapped to risk ?
    # payment_type was mapped to payment_type_risk, so we can keep risk and drop raw type if encoded, or keep raw if pipeline handles categorical.
    # mlapp handles categorical.
    
    # Let's clean up X based on intuition if we can't see full notebook drop list.
    # 'payment_type' -> categorical.
    # 'from_acc', 'to_acc' -> likely high cardinality ID.
    
    # Dropping clearly ID interactions if we have the aggregates.
    # But graph features rely on them... wait, graph features are ALREADY calculated in df_processed.
    # So we don't need the raw IDs for the model anymore.
    
    cols_to_drop = [c for c in ['from_acc', 'to_acc', 'from_bank', 'to_bank'] if c in X.columns]
    print(f"Dropping ID columns: {cols_to_drop}")
    X = X.drop(columns=cols_to_drop)

    print("Data types in X:")
    print(X.dtypes)
    print("Sample of X:")
    print(X.head())

    from src.train import train_all_models, print_results
    print("Running training pipeline...")
    print(f"Training features: {X.columns.tolist()}")
    
    results = train_all_models(X, y, n_iter=args.n_iter, model_name=args.model)
    
    print_results(results)

if __name__ == "__main__":
    main()
