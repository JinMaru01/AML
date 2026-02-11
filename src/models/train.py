import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")

def get_model_configs():
    from mlapp.ml.classification import LightGBM, DecisionTree, SVC
    return {
        "lightgbm": {
            "class": LightGBM,
            "params": {
                "num_leaves": [32],
                "max_depth": [6],
                "learning_rate": [0.03],
                "n_estimators": [1000],
                "scale_pos_weight": [200],
            },
        },
        "decision_tree": {
            "class": DecisionTree,
            "params": {
                "max_depth": [4, 6, 8],
                "min_samples_leaf": [50, 100],
            },
        },
        "svc": {
            "class": SVC,
            "params": {
                "kernel": ["rbf"],
                "C": [0.1, 1, 10],
                "gamma": ["scale"],
            },
        },
    }

def build_pipeline(model):
    """
    Builds the preprocessing pipeline for the model.
    """
    try:
        model.data_pipeline.schema(enforce=True) \
            .infer_columns() \
            .impute(add_missing_indicators=True) \
            .rare_categories(min_freq=2) \
            .outliers(method="quantile", low_q=0.01, high_q=0.9) \
            .multicollinearity_corr(threshold=0.8) \
            .build()
    except Exception as e:
        print(f"Warning: Issue building pipeline for {model}: {e}")

def run_model(model_cls, params, X, y, n_iter=50):
    """
    Instantiates, tunes, and trains a model.
    """
    model = model_cls()
    
    if hasattr(model, 'set_tuning_params'):
        model.set_tuning_params(**params)
    
    build_pipeline(model)

    X_test, y_test = model.fit(
        X,
        y,
        search_method="optuna",
        tuning_params=model.tuning_params if hasattr(model, 'tuning_params') else None,
        n_iter=n_iter,
    )

    return model, X_test, y_test

def evaluate_model(model, X_test, y_test, keys=None):
    """
    Predict and compute metrics for a model.
    """
    y_pred = model.predict(X_test)

    try:
        y_pred_proba = model.predict_proba(X_test)
    except AttributeError:
        y_pred_proba = None

    metric_keys = keys or [
        "accuracy",
        "confusion_matrix",
        "f1",
        "recall_sensitivity"
    ]
    
    metrics = model.build_metrics(
        y_test=y_test,
        y_pred=y_pred,
        keys=metric_keys
    )

    return {
        "y_pred": y_pred,
        "y_pred_proba": y_pred_proba,
        "metrics": metrics
    }

def train_all_models(X, y, n_iter=10, model_name="all"):
    """
    Train and evaluate configured models.
    """
    results = {}
    configs = get_model_configs()
    
    if model_name != "all":
        if model_name in configs:
            configs = {model_name: configs[model_name]}
        else:
            print(f"Warning: Model {model_name} not found in configs. Available: {list(configs.keys())}")
            return results

    for name, cfg in configs.items():
        print(f"\n🚀 Training {name.upper()}")
        try:
            model, X_test, y_test = run_model(
                model_cls=cfg["class"],
                params=cfg["params"],
                X=X,
                y=y,
                n_iter=n_iter,
            )
            
            # Evaluate
            eval_result = evaluate_model(model, X_test, y_test)
            
            results[name] = {
                "model": model,
                "metrics": eval_result["metrics"],
                "X_test": X_test,
                "y_test": y_test
            }
        except Exception as e:
            print(f"Error training {name}: {e}")
            import traceback
            traceback.print_exc()
            
    return results

def print_results(results):
    print("\n📊 MODEL COMPARISON")
    for name, res in results.items():
        m = res["metrics"]
        try:
            # Handling nested dictionaries as seen in notebook output key error
            # Notebook output suggested m['recall_sensitivity']['binary']
            # We use safe get to handle potential structure differences
            
            recall = "N/A"
            if 'recall_sensitivity' in m:
                if isinstance(m['recall_sensitivity'], dict) and 'binary' in m['recall_sensitivity']:
                    recall = m['recall_sensitivity']['binary']
                else:
                    recall = m['recall_sensitivity']
            
            f1 = "N/A"
            if 'f1' in m:
                if isinstance(m['f1'], dict) and 'binary' in m['f1']:
                    f1 = m['f1']['binary']
                else:
                    f1 = m['f1']
            
            acc = m.get('accuracy', 'N/A')
            
            # Formatting
            recall_str = f"{recall:.4f}" if isinstance(recall, (int, float)) else str(recall)
            f1_str = f"{f1:.4f}" if isinstance(f1, (int, float)) else str(f1)
            acc_str = f"{acc:.4f}" if isinstance(acc, (int, float)) else str(acc)

            print(
                f"{name.upper():15s} | "
                f"Recall: {recall_str} | "
                f"F1: {f1_str} | "
                f"Acc: {acc_str}"
            )
        except Exception as e:
            print(f"Could not print complete metrics for {name}: {e}")
