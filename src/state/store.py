import abc
import datetime
from collections import defaultdict, deque

class StateStore(abc.ABC):
    @abc.abstractmethod
    def get_account_state(self, account_id):
        """Retrieve the current FSM state of an account."""
        pass

    @abc.abstractmethod
    def update_account_state(self, account_id, state):
        """Update the FSM state of an account."""
        pass

    @abc.abstractmethod
    def add_transaction(self, account_id, transaction):
        """Add a transaction to the account's history."""
        pass

    @abc.abstractmethod
    def get_history(self, account_id):
        """Retrieve transaction history for an account."""
        pass
    
    @abc.abstractmethod
    def get_start_timestamp(self):
        """Get the timestamp of the first transaction seen."""
        pass

class InMemoryStateStore(StateStore):
    def __init__(self, history_limit=100):
        self.states = defaultdict(lambda: "NORMAL")
        self.history = defaultdict(lambda: deque(maxlen=history_limit))
        self.counters = defaultdict(lambda: defaultdict(float))
        self.start_timestamp = None

    def get_account_state(self, account_id):
        return self.states[account_id]

    def update_account_state(self, account_id, state):
        self.states[account_id] = state

    def add_transaction(self, account_id, transaction):
        self.history[account_id].append(transaction)
        
        # Track earliest timestamp seen for global time reference if needed
        ts = transaction.get('timestamp')
        if ts:
             # Assuming ts is comparable or converting here if strictly needed
             pass

    def get_history(self, account_id):
        return list(self.history[account_id])
        
    def get_start_timestamp(self):
        # In a real stream, we might track window start. 
        # For simulation, we might rely on the pipeline to manage time.
        return self.start_timestamp
