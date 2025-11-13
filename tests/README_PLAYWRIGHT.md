# Playwright Testing for ASEAGI

This directory contains Playwright end-to-end tests for web scraping and automated browser testing.

## Overview

Playwright is a modern browser automation framework that allows you to:
- Scrape dynamic websites that require JavaScript
- Test web applications across multiple browsers (Chromium, Firefox, WebKit)
- Capture screenshots and videos
- Test responsive designs
- Monitor website accessibility

## Setup

### 1. Install Dependencies

All required packages are in `requirements.txt`:

```bash
pip install -r requirements.txt
```

This installs:
- `pytest==7.4.3` - Testing framework
- `pytest-playwright==0.4.3` - Playwright pytest plugin
- `playwright==1.40.0` - Browser automation library

### 2. Install Browser Binaries

After installing Python packages, you need to download the browser binaries:

```bash
# Install Chromium only (recommended for headless testing)
playwright install chromium

# Or install all browsers
playwright install

# Or install with system dependencies (may require sudo)
playwright install --with-deps chromium
```

**Note:** Browser downloads require internet access and may be blocked by some firewalls or proxy configurations. If you're on a restricted network, you may need to run this on a server with unrestricted internet access (e.g., Digital Ocean droplet).

## Test Files

### `test_odpem_website.py`

Comprehensive test suite for the ODPEM Jamaica website (https://www.odpem.org.jm/).

**Test Coverage:**
- Homepage loading and accessibility
- Navigation menu structure
- Contact information presence
- Footer elements
- Page load performance
- Console error detection
- Mobile responsiveness
- Image loading validation
- External link validation
- Search functionality
- Basic accessibility checks (alt text, heading structure)
- Emergency-related content verification

## Running Tests

### Run All Playwright Tests

```bash
# Run all playwright-marked tests
pytest tests/test_odpem_website.py -v -m playwright

# Or simply
pytest tests/test_odpem_website.py -v
```

### Run Specific Test Classes

```bash
# Test website structure only
pytest tests/test_odpem_website.py::TestODPEMWebsite -v

# Test content only
pytest tests/test_odpem_website.py::TestODPEMContent -v
```

### Run Specific Test

```bash
pytest tests/test_odpem_website.py::TestODPEMWebsite::test_homepage_loads -v
```

### Run with Different Browsers

By default, tests run on Chromium. To test on multiple browsers:

```bash
# Firefox
pytest tests/test_odpem_website.py --browser firefox

# WebKit (Safari)
pytest tests/test_odpem_website.py --browser webkit

# All browsers
pytest tests/test_odpem_website.py --browser chromium --browser firefox --browser webkit
```

### Run in Headed Mode (See the Browser)

```bash
pytest tests/test_odpem_website.py --headed
```

### Generate Test Report

```bash
# HTML report
pytest tests/test_odpem_website.py --html=report.html --self-contained-html

# JUnit XML (for CI/CD)
pytest tests/test_odpem_website.py --junitxml=test-results.xml
```

## Configuration

### Pytest Configuration (`pytest.ini`)

Located at `/home/user/ASEAGI/pytest.ini`:

```ini
[pytest]
testpaths = tests
addopts = -v --tb=short --strict-markers --color=yes
markers =
    playwright: Playwright browser tests
    slow: Tests that take a long time to run
```

### Playwright Fixtures (`conftest.py`)

Located at `/home/user/ASEAGI/tests/conftest.py`:

**Key Fixtures:**
- `browser_context_args` - Configures browser viewport and user agent
- `playwright_browser_launch_args` - Sets headless mode and browser flags
- `base_url` - Base URL for local Streamlit dashboards
- `odpem_url` - ODPEM website URL

**Customization:**
```python
# Change viewport size
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080}
    }

# Run in headed mode by default
@pytest.fixture(scope="session")
def playwright_browser_launch_args():
    return {"headless": False}
```

## Web Scraping Examples

### Basic Page Scraping

```python
def test_scrape_page_content(page, odpem_url):
    """Scrape all text content from ODPEM website"""
    page.goto(odpem_url)

    # Get all visible text
    page_text = page.locator("body").inner_text()

    # Get specific elements
    headlines = page.locator("h1, h2, h3").all()
    for headline in headlines:
        print(headline.inner_text())
```

### Extract Structured Data

```python
def test_extract_contact_info(page, odpem_url):
    """Extract contact information from webpage"""
    page.goto(odpem_url)

    content = page.content()

    # Find emails
    import re
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)

    # Find phone numbers
    phones = re.findall(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', content)

    assert len(emails) > 0, "No emails found"
    assert len(phones) > 0, "No phone numbers found"
```

### Take Screenshots

```python
def test_screenshot_capture(page, odpem_url):
    """Capture screenshot of webpage"""
    page.goto(odpem_url)

    # Full page screenshot
    page.screenshot(path="odpem_full.png", full_page=True)

    # Specific element screenshot
    header = page.locator("header").first
    header.screenshot(path="odpem_header.png")
```

### Wait for Dynamic Content

```python
def test_dynamic_content(page, odpem_url):
    """Wait for JavaScript-loaded content"""
    page.goto(odpem_url)

    # Wait for specific element
    page.wait_for_selector(".news-feed", timeout=10000)

    # Wait for network to be idle
    page.wait_for_load_state("networkidle")

    # Wait for specific text
    page.wait_for_selector("text=Emergency Alerts")
```

## Deployment on Digital Ocean Droplet

### Initial Setup

```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Update system
apt update && apt upgrade -y

# Install Python and pip
apt install python3 python3-pip -y

# Clone repository
git clone https://github.com/dondada876/ASEAGI.git
cd ASEAGI

# Install Python dependencies
pip3 install -r requirements.txt

# Install Playwright browsers with system dependencies
playwright install --with-deps chromium
```

### Running Tests on Droplet

```bash
# Run tests
python3 -m pytest tests/test_odpem_website.py -v

# Run in background with nohup
nohup python3 -m pytest tests/test_odpem_website.py -v > test_output.log 2>&1 &

# View logs
tail -f test_output.log
```

### Scheduled Testing with Cron

```bash
# Edit crontab
crontab -e

# Add daily test run at 2 AM
0 2 * * * cd /root/ASEAGI && /usr/bin/python3 -m pytest tests/test_odpem_website.py -v >> /var/log/odpem_tests.log 2>&1
```

## Continuous Integration (CI/CD)

### GitHub Actions Example

Create `.github/workflows/playwright-tests.yml`:

```yaml
name: Playwright Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install --with-deps chromium

      - name: Run Playwright tests
        run: |
          pytest tests/test_odpem_website.py -v --junitxml=test-results.xml

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: test-results.xml
```

## Troubleshooting

### Browser Download Fails (403 Forbidden)

**Symptom:** `Error: Download failed: server returned code 403`

**Solution:**
1. Check internet connectivity
2. Try different network (not behind corporate firewall/proxy)
3. Use environment variable for custom download server:
   ```bash
   export PLAYWRIGHT_DOWNLOAD_HOST=https://alternative-cdn.com
   playwright install chromium
   ```
4. Run on unrestricted server (e.g., Digital Ocean droplet)

### Tests Fail with "Executable doesn't exist"

**Symptom:** `Executable doesn't exist at /root/.cache/ms-playwright/chromium-*/chrome`

**Solution:**
```bash
playwright install chromium
```

### System Dependencies Missing

**Symptom:** Browser launches but crashes immediately

**Solution:**
```bash
# Install with system dependencies
playwright install --with-deps chromium

# Or manually install dependencies (Ubuntu/Debian)
apt-get install -y \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libgbm1 \
    libasound2
```

### Headless Mode Issues

**Symptom:** Tests pass in headed mode but fail in headless

**Solution:**
Add to `conftest.py`:
```python
@pytest.fixture(scope="session")
def playwright_browser_launch_args():
    return {
        "headless": True,
        "args": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu"
        ]
    }
```

## Best Practices

1. **Use Page Object Model** - Separate page interactions into reusable classes
2. **Add Wait Strategies** - Always wait for elements before interacting
3. **Handle Timeouts Gracefully** - Set appropriate timeouts for slow networks
4. **Capture Artifacts on Failure** - Save screenshots/videos when tests fail
5. **Run Headless in CI** - Use headed mode only for local debugging
6. **Parallelize Tests** - Use pytest-xdist for faster execution
7. **Mock External Services** - Avoid flaky tests from third-party dependencies

## Performance Tips

```bash
# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest tests/ -n 4  # 4 parallel workers

# Run only fast tests during development
pytest tests/ -m "not slow"

# Generate tracing for debugging
pytest tests/ --tracing on --screenshot on --video on
```

## Resources

- **Playwright Python Docs:** https://playwright.dev/python/
- **pytest-playwright Plugin:** https://github.com/microsoft/playwright-pytest
- **Playwright Discord:** https://discord.gg/playwright
- **Examples Repository:** https://github.com/microsoft/playwright-python

## Support

For issues or questions:
1. Check this README
2. Review Playwright documentation
3. Check project GitHub Issues
4. Contact project maintainers

---

**Last Updated:** November 13, 2025
**Playwright Version:** 1.40.0
**pytest-playwright Version:** 0.4.3
