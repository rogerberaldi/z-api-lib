"""
Basic usage example for zapi_async.

This example demonstrates how to:
- Initialize the client
- Check connection status
- Send different types of messages
"""

import asyncio
import os
from zapi_async import ZAPIClient


async def main():
    # Get credentials from environment variables
    instance_id = os.getenv("ZAPI_INSTANCE_ID", "YOUR_INSTANCE_ID")
    token = os.getenv("ZAPI_TOKEN", "YOUR_TOKEN")
    client_token = os.getenv("ZAPI_CLIENT_TOKEN", "YOUR_CLIENT_TOKEN")
    
    # Phone number to send messages to
    phone = os.getenv("ZAPI_TEST_PHONE", "5511999999999")
    
    # Initialize client
    async with ZAPIClient(
        instance_id=instance_id,
        token=token,
        client_token=client_token,
    ) as client:
        
        print("="*50)
        print("Z-API Async - Basic Usage Example")
        print("="*50)
        
        # 1. Check connection status
        print("\n1. Checking connection status...")
        status = await client.get_status()
        print(f"   Connected: {status.connected}")
        if status.connected:
            print(f"   Phone: {status.phone}")
        else:
            print("   ⚠️  Instance not connected! Please connect first.")
            print("   Get QR code with: await client.get_qrcode(image=True)")
            return
        
        # 2. Send text message
        print("\n2. Sending text message...")
        result = await client.send_text(
            phone=phone,
            message="Hello from *Z-API*! 🚀\n\nThis is a _test message_ with ~formatting~."
        )
        print(f"   ✅ Message sent! ID: {result.message_id}")
        
        # 3. Send image from URL
        print("\n3. Sending image from URL...")
        result = await client.send_image(
            phone=phone,
            image="https://www.z-api.io/wp-content/themes/z-api/dist/images/logo.svg",
            caption="Z-API Logo 🎨"
        )
        print(f"   ✅ Image sent! ID: {result.message_id}")
        
        # 4. Send with typing delay
        print("\n4. Sending message with typing indicator...")
        result = await client.send_text(
            phone=phone,
            message="This message showed 'typing...' for 3 seconds ⌨️",
            delay_typing=3,
        )
        print(f"   ✅ Message sent! ID: {result.message_id}")
        
        print("\n" + "="*50)
        print("All messages sent successfully!")
        print("="*50)


if __name__ == "__main__":
    asyncio.run(main())
