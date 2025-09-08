"""
Pytest configuration and fixtures.
Sets up common test utilities and environment.
"""
import sys
import os
import asyncio

# Add src directory to Python path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()