
from freezegun import freeze_time
from chalicelib.circuit_breaker import CircuitBreakerCore


def test_cb_arms_after_5_failures():
    cb = CircuitBreakerCore('test_service', None)
    assert cb.is_armed()
    
    cb.register_failure()
    assert cb.is_armed()
    assert cb._current_state.get('counter') == 1
    
    cb.register_failure()
    assert cb.is_armed()
    assert cb._current_state.get('counter') == 2
    
    cb.register_failure()
    assert cb.is_armed()
    assert cb._current_state.get('counter') == 3
    
    cb.register_failure()
    assert cb.is_armed()
    assert cb._current_state.get('counter') == 4
    
    cb.register_failure()
    assert cb._current_state.get('counter') == 5
    assert cb.is_armed() is False

def test_cb_resets_after_failure_window_expires():
    cb = CircuitBreakerCore('test_service', None)
    assert cb.is_armed()

    with freeze_time("2012-01-14 03:21:34"):
        cb.register_failure()
        assert cb.is_armed()
        
        cb.register_failure()
        assert cb.is_armed()
        
        cb.register_failure()
        assert cb.is_armed()
        
        cb.register_failure()
        assert cb.is_armed()

    with freeze_time("2012-01-14 03:27:34"): # 6 minutes later
        cb.register_failure()
        assert cb.is_armed()
        assert cb._current_state.get('counter') == 1

def test_cb_resets_after_failure_window_expires_without_armed_test():
    cb = CircuitBreakerCore('test_service', None)
    assert cb.is_armed()

    with freeze_time("2012-01-14 03:21:34"):
        cb.register_failure()
        assert cb.is_armed()
        
        cb.register_failure()
        assert cb.is_armed()
        
        cb.register_failure()
        assert cb.is_armed()
        
        cb.register_failure()
        assert cb.is_armed()

    with freeze_time("2012-01-14 03:27:34"): # 6 minutes later
        cb.register_failure()
        assert cb._current_state.get('counter') == 1

