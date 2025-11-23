# Z-API Async

🚀 **Async Python library for Z-API WhatsApp service**

A modern, fully-typed async Python wrapper for the Z-API WhatsApp service, inspired by `pywa_async`.

## Features

- ✅ **Fully Async** - Built with `asyncio` and `httpx`
- ✅ **Type Safe** - Complete type hints for all methods
- ✅ **Easy to Use** - Clean, intuitive API
- ✅ **Comprehensive** - Supports all Z-API message types
- ✅ **Well Documented** - Extensive docstrings and examples
- ✅ **Tested** - Integration tests with FastAPI

## Installation

```bash
pip install zapi-async
```

Or for development:

```bash
git clone https://github.com/yourusername/zapi-async.git
cd zapi-async
pip install -e ".[dev]"
```

## Quick Start

```python
import asyncio
from zapi_async import ZAPIClient

async def main():
    # Initialize client
    client = ZAPIClient(
        instance_id="YOUR_INSTANCE_ID",
        token="YOUR_TOKEN",
        client_token="YOUR_CLIENT_TOKEN"  # Optional but recommended
    )
    
    # Check connection status
    status = await client.get_status()
    print(f"Connected: {status.connected}")
    
    # Send a text message
    result = await client.send_text(
        phone="5511999999999",
        message="Hello from Z-API! *This is bold* and _this is italic_"
    )
    print(f"Message sent: {result.message_id}")
    
    # Send an image
    result = await client.send_image(
        phone="5511999999999",
        image="https://example.com/image.jpg",
        caption="Check this out!"
    )
    
    # Close client
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Authentication

Z-API uses instance-based authentication:

1. **Instance ID**: Your Z-API instance identifier
2. **Token**: Your instance token
3. **Client Token**: Optional security token (recommended)

Get these credentials from your [Z-API dashboard](https://developer.z-api.io/).

## Sending Messages

### Text Messages

```python
# Simple text
await client.send_text(
    phone="5511999999999",
    message="Hello!"
)

# With formatting
await client.send_text(
    phone="5511999999999",
    message="*Bold* _italic_ ~strikethrough~ ```monospace```"
)

# With delays
await client.send_text(
    phone="5511999999999",
    message="Hello!",
    delay_typing=3,  # Show "typing..." for 3 seconds
    delay_message=2   # Wait 2 seconds before sending
)
```

### Media Messages

```python
# Image from URL
await client.send_image(
    phone="5511999999999",
    image="https://example.com/image.jpg",
    caption="Beautiful picture!"
)

# Image from file
await client.send_image(
    phone="5511999999999",
    image="/path/to/image.jpg",
    view_once=True  # View once mode
)

# Video
await client.send_video(
    phone="5511999999999",
    video="https://example.com/video.mp4",
    caption="Check this video"
)

# Document
await client.send_document(
    phone="5511999999999",
    document="/path/to/document.pdf",
    filename="report.pdf"
)

# Audio
await client.send_audio(
    phone="5511999999999",
    audio="/path/to/audio.mp3"
)

# Sticker
await client.send_sticker(
    phone="5511999999999",
    sticker="/path/to/sticker.webp"
)
```

## Instance Management

```python
# Get connection status
status = await client.get_status()
if status.connected:
    print(f"Connected as: {status.phone}")

# Get QR code for connection
qr = await client.get_qrcode(image=True)
# Display qr.image in your UI

# Get phone code (alternative to QR)
code = await client.get_phone_code("5511999999999")
print(f"Enter this code in WhatsApp: {code.code}")

# Disconnect
await client.disconnect()
```

## Using Context Manager

```python
async with ZAPIClient(
    instance_id="YOUR_INSTANCE_ID",
    token="YOUR_TOKEN",
    client_token="YOUR_CLIENT_TOKEN"
) as client:
    await client.send_text("5511999999999", "Hello!")
    # Client automatically closes
```

## Error Handling

```python
from zapi_async import (
    ZAPIError,
    AuthenticationError,
    InstanceError,
    MessageError,
)

try:
    await client.send_text("5511999999999", "Hello!")
except AuthenticationError:
    print("Invalid credentials")
except InstanceError:
    print("Instance not connected")
except MessageError as e:
    print(f"Failed to send message: {e}")
except ZAPIError as e:
    print(f"API error: {e}")
```

## Phone Number Format

Z-API expects phone numbers in international format without symbols:
- ✅ `5511999999999` (DDI + DDD + NUMBER)
- ❌ `+55 11 99999-9999`
- ❌ `(11) 99999-9999`

The library automatically formats phone numbers for you.

## Development

```bash
# Install development dependencies
pip install -e ".[dev,test]"

# Run tests
pytest

# Run type checking
mypy zapi_async/

# Format code
black zapi_async/
```

## Examples

See the `examples/` directory for more examples:
- `basic_usage.py` - Basic client usage
- `webhook_server.py` - Webhook server with FastAPI

## Documentation

For complete API documentation, see the [Z-API official docs](https://developer.z-api.io/).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Credits

- Inspired by [pywa_async](https://github.com/david-lev/pywa)
- Built for [Z-API](https://www.z-api.io/)

## Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/yourusername/zapi-async/issues)
- Check [Z-API documentation](https://developer.z-api.io/)
