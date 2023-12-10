
from datetime import datetime
import os
from typing import Union

from chalicelib.store import DynamoDBStorage


class CircuitBreakerCore:
    def __init__(self, service_name: str, current_state: Union[dict, None]):
        self._service_name = service_name
        self._current_state = current_state
        self._failure_window_in_minutes = os.environ.get('failure_window_in_minutes', 5)
        self._disarm_threshold = os.environ.get('disarm_threshold', 5)

    def is_armed(self):
        if self._has_reached_failures_limit():
            return False
        if not self._is_failure_window_active() and self._current_state:
            self._clean_registry()
        return True

    def register_failure(self):
        if not self._current_state or not self._is_failure_window_active():
            new_state = {
                'service_name': self._service_name,
                'timestamp': datetime.now(),
                'counter': 1
            }
        else:
            new_state = self._current_state
            new_state.update(
                {'counter': self._current_state['counter']+1}
            )
        self._current_state = new_state
        return new_state

    def _has_reached_failures_limit(self):
        return self._is_failure_window_active() \
            and self._failure_count_exceeds_threshold()
    
    def _is_failure_window_active(self):
        if self._current_state:
            failure_window_start_timestamp = self._current_state.get('timestamp')
            now = datetime.now()
            failure_window_in_seconds = (now - failure_window_start_timestamp).seconds
            return failure_window_in_seconds < self._failure_window_in_minutes*60
        return False

    def _failure_count_exceeds_threshold(self):
        counter = self._current_state.get('counter')
        return counter >= self._disarm_threshold

    def _clean_registry(self):
        self._current_state = None


class CircuitBreakerDynamoDB(CircuitBreakerCore):
    def __init__(self, service_name: str):
        self._dynamodb_storage = DynamoDBStorage()
        current_state = self._dynamodb_storage.get_current_state(service_name)
        if current_state:
            current_state.update(
                {'timestamp': datetime.strptime(current_state['timestamp'], "%Y-%m-%d %H:%M:%S")}
            )
        super().__init__(service_name, current_state)

    def register_failure(self):
        new_state = super().register_failure()
        new_state.update(
            {'timestamp': new_state['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
        )
        self._dynamodb_storage.set_new_state(new_state)

    def _clean_registry(self):
        self._dynamodb_storage.delete_current_state(self._service_name)
        return super()._clean_registry()
    