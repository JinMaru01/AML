import pandas as pd
import numpy as np
import argparse
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import warnings
warnings.filterwarnings("ignore")

from src.state.store import InMemoryStateStore
from src.logic.vadalog_engine import VadalogEngine
from src.logic.automata import Automata
from src.models.anomaly import AnomalyDetector
from src.features import load_data, preprocess_features

def run_pipeline(trans_path, acc_path, output_path):
    print("Initializing Hybrid System...")
    store = InMemoryStateStore()
    vadalog = VadalogEngine(store)
    fsm = Automata(store)
    anomaly_detector = AnomalyDetector()

    print("Loading Data...")
    df_trans, df_acc = load_data(trans_path, acc_path)
    
    # Pre-train anomaly detector on the first batch (simulated historical data)
    # In real-time, this would be a pre-trained model loaded from disk
    print("Training Anomaly Detector on batch...")
    # Using 'amount' and maybe 'hour' for simple anomaly detection
    features_for_anomaly = df_trans[['amount', 'hour']].fillna(0)
    anomaly_detector.train(features_for_anomaly)

    print("Processing Transactions Stream...")
    alerts = []
    
    # Simulating stream processing
    # Sort by timestamp to simulate order
    df_trans = df_trans.sort_values('timestamp')
    
    # Iterate (for a real large dataset, we would use a true stream or batching)
    # For demo, taking a subset or iterating efficiently
    
    for idx, row in df_trans.iterrows():
        account_id = row['from_acc']
        tx_data = row.to_dict()
        
        # 1. Update State Store
        store.add_transaction(account_id, tx_data)
        
        # 2. Update Feature Context (Mocking feature calculation per tx)
        # In production, this would fetch aggregates from Redis
        history = store.get_history(account_id)
        current_features = {
            'tx_count_24h': len(history), # Mocking 24h as 'all history' for this snippet
            'avg_amount_24h': np.mean([t['amount'] for t in history]),
            'velocity_score': 0.5 # Mock
        }

        # 3. Reasoning & Logic (Vadalog)
        vadalog.update_knowledge_graph(tx_data)
        risk_score_logic, risk_reasons = vadalog.infer_risk_scores(account_id)
        
        # 4. Automata Transition
        current_state = store.get_account_state(account_id)
        next_state = fsm.transition(account_id, current_state, current_features, risk_score_logic)
        
        # 5. Anomaly Score
        # Reshape for single sample
        feat_vector = np.array([[row['amount'], row['hour']]])
        anomaly_score = anomaly_detector.score(feat_vector)[0]
        
        # 6. Final Decision
        # Alert if High Risk State OR High Anomaly Score
        if next_state == Automata.STATE_HIGH_RISK or anomaly_score > 0.8:
            alert = {
                'timestamp': row['timestamp'],
                'account': account_id,
                'state': next_state,
                'logic_risk': risk_score_logic,
                'anomaly_score': anomaly_score,
                'reasons': risk_reasons
            }
            alerts.append(alert)
            if len(alerts) % 100 == 0:
                print(f"Generated {len(alerts)} alerts so far...")

    print(f"Total Alerts: {len(alerts)}")
    df_alerts = pd.DataFrame(alerts)
    df_alerts.to_csv(output_path, index=False)
    print(f"Alerts saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("--trans", default="data/LI-Small_Trans.csv")
    parser.add_argument("--trans", default="data/sample500.csv")
    parser.add_argument("--acc", default="data/LI-Small_accounts.csv")
    parser.add_argument("--out", default="hybrid_alerts.csv")
    args = parser.parse_args()
    
    run_pipeline(args.trans, args.acc, args.out)
