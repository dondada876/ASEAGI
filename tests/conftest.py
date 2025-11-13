"""
Pytest configuration and fixtures for ASEAGI tests
"""
import pytest
import os
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Configure browser context for Playwright tests
    """
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }


@pytest.fixture(scope="session")
def playwright_browser_launch_args():
    """
    Configure browser launch arguments
    """
    return {
        "headless": True,  # Set to False for debugging
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ]
    }


@pytest.fixture(scope="session")
def base_url():
    """Base URL for web application testing"""
    return os.environ.get("BASE_URL", "http://localhost:8501")


@pytest.fixture(scope="session")
def odpem_url():
    """URL for ODPEM website testing"""
    return "https://www.odpem.org.jm/"
