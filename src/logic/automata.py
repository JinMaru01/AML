class Automata:
    """
    Finite State Machine for Account behavior.
    States: NORMAL -> STRUCTURING -> LAYERING -> HIGH_RISK
    """
    STATE_NORMAL = "NORMAL"
    STATE_STRUCTURING = "STRUCTURING"
    STATE_LAYERING = "LAYERING"
    STATE_HIGH_RISK = "HIGH_RISK"

    def __init__(self, state_store):
        self.store = state_store

    def transition(self, account_id, current_state, features, risk_score):
        """
        Determine next state based on current state, features, and reasoning risk score.
        """
        next_state = current_state

        # Transition Logic
        if current_state == self.STATE_NORMAL:
            # Rule: Structuring if high frequency of small txs (fan-in or count)
            if features.get('tx_count_24h', 0) > 10 and features.get('avg_amount_24h', 0) < 1000:
                next_state = self.STATE_STRUCTURING
            # Direct jump to High Risk if Vadalog found a strong link
            elif risk_score > 0.8:
                next_state = self.STATE_HIGH_RISK

        elif current_state == self.STATE_STRUCTURING:
            # Rule: Layering if rapid movement (velocity) or high integration risk
            if features.get('velocity_score', 0) > 0.9:
                next_state = self.STATE_LAYERING
            # Back to Normal if quiet
            elif features.get('tx_count_7d', 0) < 5:
                next_state = self.STATE_NORMAL

        elif current_state == self.STATE_LAYERING:
            # Rule: High Risk if specific patterns persist or Vadalog confirms cycle
            if risk_score > 0.6 or features.get('is_cycle', False):
                next_state = self.STATE_HIGH_RISK

        # Persistence
        if next_state != current_state:
            print(f"State Transition for {account_id}: {current_state} -> {next_state}")
            self.store.update_account_state(account_id, next_state)

        return next_state
