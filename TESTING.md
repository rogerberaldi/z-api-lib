# Testing Guide for zapi_async

Comprehensive testing documentation for the zapi_async library.

## 📊 Test Coverage

### Test Suites

| Suite | File | Tests | Coverage |
|-------|------|-------|----------|
| **Client Tests** | `test_client.py` | 30+ | All client methods |
| **Webhook Tests** | `test_webhooks.py` | 20+ | All message types |
| **Helper Tests** | `test_helpers.py` | 35+ | All utilities |
| **Integration Tests** | `test_integration.py` | 10+ | Real API calls |

**Total: 95+ tests**

---

## 🚀 Quick Start

### Run All Unit Tests (Fast)

```bash
# Using pytest directly
pytest tests/ -m "unit" -v

# Using test runner
python run_tests.py unit
```

### Run With Coverage

```bash
python run_tests.py coverage

# View HTML report
open htmlcov/index.html
```

### Run Specific Test Suite

```bash
# Webhook tests only
python run_tests.py webhook

# Helper tests only
python run_tests.py helpers

# Client tests only
pytest tests/test_client.py -v
```

---

## 🔧 Test Runner Commands

The `run_tests.py` script provides convenient commands:

```bash
python run_tests.py <command>
```

### Available Commands

| Command | Description | Speed |
|---------|-------------|-------|
| `unit` | Unit tests only (mocked) | ⚡ Fast |
| `webhook` | Webhook parsing tests | ⚡ Fast |
| `helpers` | Helper function tests | ⚡ Fast |
| `integration` | Real API calls | 🐌 Slow |
| `all` | All tests except integration | ⚡ Fast |
| `fast` | Skip slow tests | ⚡ Very Fast |
| `coverage` | Run with coverage report | ⚡ Fast |
| `verbose` | Maximum verbosity + debug logs | 📝 Detailed |

---

## 🧪 Test Types

### 1. Unit Tests (Mocked)

Fast tests with no external dependencies. All API calls are mocked.

```bash
pytest -m unit -v
```

**Features:**
- ✅ All HTTP requests mocked
- ✅ No external dependencies
- ✅ Fast execution (~2-5 seconds)
- ✅ Detailed logging

**Example test:**
```python
async def test_send_text(mock_client, test_phone):
    result = await mock_client.send_text(test_phone, "Hello")
    assert result.message_id is not None
```

### 2. Webhook Tests

Test webhook payload parsing and message type detection.

```bash
pytest tests/test_webhooks.py -v
```

**Covers:**
- ✅ All 9 message types
- ✅ Type detection
- ✅ Field extraction
- ✅ Edge cases
- ✅ API typos handling

### 3. Helper Tests

Test utility functions (phone formatting, base64, etc.).

```bash
pytest tests/test_helpers.py -v
```

**Covers:**
- ✅ Phone number formatting
- ✅ URL validation
- ✅ Base64 detection
- ✅ MIME type detection
- ✅ Group ID detection
- ✅ Text formatting

### 4. Integration Tests (Real API)

**⚠️ WARNING:** Makes real API calls!

```bash
# Set credentials first
export ZAPI_INSTANCE_ID="your_instance"
export ZAPI_TOKEN="your_token"
export ZAPI_CLIENT_TOKEN="your_client_token"
export ZAPI_TEST_PHONE="5511999999999"

# Run integration tests
python run_tests.py integration
```

**Tests:**
- ✅ Real connection status
- ✅ Real message sending
- ✅ Real interactive messages
- ✅ Error handling
- ✅ Concurrent requests

---

## 📝 Detailed Logging

All tests include comprehensive logging.

### Log Levels

```python
# pytest.ini configures:
log_cli_level = INFO       # Console output
log_file_level = DEBUG     # File output (tests/test_log.txt)
```

### Example Log Output

```
2025-11-22 14:00:00 [    INFO] 🧪 Testing send_text (basic)
2025-11-22 14:00:00 [   DEBUG] 📡 Mock HTTP request: POST /send-text
2025-11-22 14:00:00 [    INFO] ✅ Text message sent successfully: TEST_MSG_ID
```

### View Logs

```bash
# During test run (console)
pytest tests/ -v -s --log-cli-level=DEBUG

# After test run (file)
cat tests/test_log.txt
```

---

##  Expert Fixtures

### Available Fixtures

Located in `tests/conftest.py`:

| Fixture | Type | Purpose |
|---------|------|---------|
| `mock_client` | Client | Mocked ZAPIClient |
| `real_client` | Client | Real ZAPIClient (integration) |
| `test_config` | Dict | Test credentials |
| `test_phone` | str | Test phone number |
| `mock_httpx_client` | Mock | Mocked HTTP client |
| `mock_sent_message_response` | Dict | Mock send response |
| `mock_webhook_text_message` | Dict | Mock webhook payload |
| `create_mock_response` | Factory | Create custom responses |
| `assert_sent_message` | Helper | Validate SentMessage |

### Fixture Usage Examples

```python
# Basic client test
async def test_something(mock_client, test_phone):
    result = await mock_client.send_text(test_phone, "Test")
    assert result is not None

# Custom mock response
def test_with_custom_response(create_mock_response):
    response = create_mock_response(200, {"success": True})
    assert response.status_code == 200

# Assertion helper
async def test_message_send(mock_client, assert_sent_message):
    result = await mock_client.send_text("5511999999999", "Hi")
    assert_sent_message(result)  # Validates all fields
```

---

## 🎯 Test Markers

Tests are organized with pytest markers:

```bash
# Run only unit tests
pytest -m unit

# Run only webhook tests
pytest -m webhook

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Combine markers
pytest -m "unit and not slow"
```

### Available Markers

- `unit` - Unit tests (fast, mocked)
- `integration` - Integration tests (real API)
- `webhook` - Webhook parsing tests
- `slow` - Slow tests (can be skipped)

---

## 📊 Coverage Reports

### Generate Coverage

```bash
pytest --cov=zapi_async --cov-report=html

# Or use test runner
python run_tests.py coverage
```

### View Reports

```bash
# Terminal report (immediate)
pytest --cov=zapi_async --cov-report=term-missing

# HTML report (detailed)
open htmlcov/index.html

# XML report (for CI/CD)
pytest --cov=zapi_async --cov-report=xml
```

### Coverage Configuration

Located in `pytest.ini`:

```ini
[coverage:run]
source = zapi_async
omit = */tests/*, */conftest.py

[coverage:report]
precision = 2
show_missing = True
```

---

## 🔍 Debugging Tests

### Run Single Test

```bash
# Specific test function
pytest tests/test_client.py::TestTextMessaging::test_send_text_basic -v

# Specific test class
pytest tests/test_client.py::TestTextMessaging -v
```

### Maximum Verbosity

```bash
pytest tests/ -vv -s --tb=long --log-cli-level=DEBUG
```

### Stop on First Failure

```bash
pytest tests/ -x  # Stop on first failure
pytest tests/ --maxfail=3  # Stop after 3 failures
```

### Run Last Failed

```bash
pytest --lf  # Run last failed tests
pytest --ff  # Run failures first, then others
```

---

## 🐛 Common Issues

### Issue: Import Errors

```bash
# Solution: Install in development mode
pip install -e .
pip install -e ".[dev,test]"
```

### Issue: Async Tests Not Running

```bash
# Solution: Install pytest-asyncio
pip install pytest-asyncio

# Check pytest.ini has:
# asyncio_mode = auto
```

### Issue: Integration Tests Fail

```bash
# Solution: Check credentials
echo $ZAPI_INSTANCE_ID
echo $ZAPI_TOKEN

# Check instance connection
python -c "import os; from zapi_async import ZAPIClient; import asyncio; asyncio.run(ZAPIClient(os.getenv('ZAPI_INSTANCE_ID'), os.getenv('ZAPI_TOKEN')).get_status())"
```

---

## 📈 CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev,test]"
      
      - name: Run tests
        run: |
          pytest tests/ -m "not integration" --cov=zapi_async --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 🎓 Best Practices

### Writing New Tests

1. **Use descriptive names**: `test_send_text_with_formatting`
2. **Add logging**: `logger.info("🧪 Testing X")`
3. **Use fixtures**: Reuse `mock_client`, `test_phone`, etc.
4. **Mark appropriately**: Add `@pytest.mark.unit` or similar
5. **Assert clearly**: Use specific assertions

### Example Test Template

```python
import pytest
import logging

logger = logging.getLogger(__name__)


@pytest.mark.unit
@pytest.mark.asyncio
class TestMyFeature:
    """Test my awesome feature."""
    
    async def test_feature_basic(self, mock_client, caplog):
        """Test basic feature functionality."""
        logger.info("🧪 Testing my feature")
        
        result = await mock_client.my_method()
        
        assert result is not None
        logger.info("✅ Feature works!")
```

---

## 📚 Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [coverage.py documentation](https://coverage.readthedocs.io/)

---

## 🎯 Test Statistics

**Current Coverage:**
- Unit Tests: 95+ tests
- Integration Tests: 10+ tests
- Code Coverage: ~85% (target: 90%)
- Execution Time: ~5-10 seconds (unit tests)

**Test Quality:**
- ✅ Comprehensive assertions
- ✅ Detailed logging
- ✅ Edge case coverage
- ✅ Integration testing
- ✅ Concurrent testing
- ✅ Error handling validation
