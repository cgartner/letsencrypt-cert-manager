"""Fixtures used in tests."""

import time
import uuid

class LambdaContextMock:
    """A partial mock of the Amazon lambda context object.

    For more info see:
        ``http://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html``
    """

    function_name = 'LAMBDANAME'
    function_version = 'LATEST'
    aws_request_id = None

    is_mock = True
    """ You can test against this if you need to detect a test environment. """

    _instantiation_time = None
    """ Used for simulating :func:`get_remaining_time_in_millis`. """

    remaining = None
    """Allows override of get_remaining_time_in_milis return value"""

    def __init__(self):
        """Initialize LambdaContextMock."""
        self._instantiation_time = time.time()
        self.aws_request_id = str(uuid.uuid4())

    def get_remaining_time_in_millis(self):
        """Return remaining time in miliseconds."""
        if self.remaining is not None:
            return self.remaining
        allowed_time = 1000 * 5  # Simulate 5 minute max lambda
        return allowed_time - int(time.time() - self._instantiation_time)
