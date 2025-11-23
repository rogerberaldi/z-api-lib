# Beginner's Guide to Testing zapi_async

This guide will walk you through setting up your environment, configuring your credentials, and running your first tests.

## 1. Environment Setup

Before running any tests, ensure you have the necessary dependencies installed.

Open your terminal in the project root directory and run:

```bash
# Install the package in editable mode with ALL test dependencies
pip install -e ".[dev,test]"
```

This installs `pytest`, `pytest-asyncio`, `pytest-cov`, and other required libraries.

## 2. Configuration

You mentioned you have your **Instance ID** and **Token**. You need to set these as environment variables so the tests can use them.

### Option A: Temporary Session (Recommended for quick tests)

Run these commands in your terminal (replace with your actual values):

```bash
export ZAPI_INSTANCE_ID="your_instance_id_here"
export ZAPI_TOKEN="your_token_here"
export ZAPI_CLIENT_TOKEN="your_client_token_here" 
# Note: Client Token is often the same as Token for some setups, or a separate security token. 
# If you don't have a separate client token, try using your regular token or check your Z-API dashboard.

# Optional: Set a test phone number to receive messages (e.g., your own WhatsApp)
# Format: CountryCode + AreaCode + Number (e.g., 5511999999999)
export ZAPI_TEST_PHONE="5511999999999"
```

### Option B: Permanent Configuration (For frequent testing)

You can add these lines to your `~/.bashrc` or `~/.zshrc` file so they persist.

## 3. Running Your First Test

Let's start with **Unit Tests**. These don't require your credentials and check if the library code is logic-correct.

```bash
python run_tests.py unit
```

**Expected Output:** You should see green text saying `✅ Unit Tests - PASSED`.

## 4. Running Integration Tests (Real API Calls)

Now, let's use your new Instance ID to test the connection.

**⚠️ WARNING:** These tests make REAL requests to the Z-API servers.

### Step 4.1: Test Connection Only

Let's run just the connection test first to verify your credentials.

```bash
pytest tests/test_integration.py::TestRealAPIConnection -v -s
```

If successful, you'll see:
- `✅ Instance is connected`
- `Status: connected`

### Step 4.2: Test Sending a Message

If the connection test passed, try sending a real message to the `ZAPI_TEST_PHONE` you configured.

```bash
pytest tests/test_integration.py::TestRealMessaging::test_send_text_real -v -s
```

Check your WhatsApp! You should receive a message: *"🧪 Test message from zapi_async integration tests"*.

## 5. Deep Analysis of Test Cases

Here is an analysis of what is being tested in the codebase:

### `tests/test_integration.py` (The Real World Tests)
This file is critical for you right now. It verifies your instance is actually working.
- **`TestRealAPIConnection`**: Calls `get_status()`. It validates that your credentials are correct and the instance is reachable.
- **`TestRealMessaging`**:
    - `test_send_text_real`: Sends a basic text. Verifies the API returns a `messageId`.
    - `test_send_location_real`: Sends a location pin. Useful to test complex payload structures.
- **`TestRealInteractiveMessages`**:
    - `test_send_button_list_real`: Sends a menu with buttons. This is a common failure point in WhatsApp APIs, so testing it ensures your interactive features work.
    - `test_send_poll_real`: Sends a voting poll.
- **`TestStressTest`**: Runs multiple status checks at once to ensure your async code handles concurrency correctly without crashing.

### `tests/test_client.py` (The Logic Tests)
These tests use "mocks" (fake servers). They are safe to run anytime.
- They check if the library *correctly constructs* the data before sending it.
- Example: If you try to send a message without a phone number, these tests ensure the library raises an error *before* even trying to call the API.

### `tests/test_webhooks.py`
- Simulates receiving messages from WhatsApp.
- Verifies that when Z-API sends you a webhook, this library can parse it into a nice Python object (`TextMessage`, `ImageMessage`, etc.) instead of just giving you raw JSON.

## Troubleshooting

- **401 Unauthorized**: Double-check your `ZAPI_INSTANCE_ID` and `ZAPI_TOKEN`.
- **Instance not connected**: Ensure your phone is actually linked to the instance via QR Code.
- **Timeout**: Check your internet connection.
