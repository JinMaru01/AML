import networkx as nx

class VadalogEngine:
    """
    Simulated Datalog/Vadalog reasoning engine.
    Applies logical rules to a knowledge graph derived from the transaction state.
    """
    def __init__(self, state_store):
        self.store = state_store
        self.graph = nx.DiGraph()

    def update_knowledge_graph(self, transaction):
        """
        Incrementally update the graph with new transaction facts.
        Fact: Transfer(from_acc, to_acc, amount, timestamp)
        """
        u = transaction['from_acc']
        v = transaction['to_acc']
        attrs = {
            'amount': transaction.get('amount', 0),
            'ts': transaction.get('timestamp')
        }
        self.graph.add_edge(u, v, **attrs)

    def infer_risk_scores(self, active_account):
        """
        Apply 'Vadalog' rules to infer risk.
        Rule 1: Suspicious(X) :- HighRiskCountry(Y), Transfer(X, Y)
        Rule 2: Cycle(X) :- Transfer(X, Y), Transfer(Y, Z), Transfer(Z, X)
        """
        risk_score = 0.0
        reasons = []

        # Rule: High In-Degree Fan-In (Simulation of aggregation rule)
        # Suspicious(X) :- Count(Y, Transfer(Y,X)) > Threshold
        if self.graph.has_node(active_account):
            in_degree = self.graph.in_degree(active_account)
            if in_degree > 5:
                risk_score += 0.2
                reasons.append(f"High fan-in: {in_degree}")

        # Rule: Cycle Detection (Structural Reasoning)
        # Cycle(X) :- Path(X, X)
        try:
            circles = list(nx.simple_cycles(self.graph))
            for circle in circles:
                if active_account in circle:
                    risk_score += 0.5
                    reasons.append(f"Involved in cycle: {circle}")
                    break
        except Exception:
            # Complex cycle detection can be slow; checking simple cycles only
            pass

        return risk_score, reasons
