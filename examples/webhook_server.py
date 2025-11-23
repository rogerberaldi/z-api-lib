"""
FastAPI webhook server example for z api_async.

This example demonstrates how to:
- Set up a FastAPI webhook endpoint
- Parse incoming webhook payloads
- Handle different message types
- Respond to messages

To run:
    pip install fastapi uvicorn
    python examples/webhook_server.py

Then configure your Z-API webhook URL to point to:
    http://your-server:8000/webhook
"""

import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

from zapi_async import (
    ZAPIClient,
    parse_webhook_message,
    is_text_message,
    is_image_message,
    is_audio_message,
    is_location_message,
    is_group_message,
    is_from_me,
    TextMessage,
    ImageMessage,
)

# Initialize FastAPI app
app = FastAPI(title="Z-API Webhook Server")

# Initialize Z-API client (for sending responses)
# In production, load these from environment variables
CLIENT = ZAPIClient(
    instance_id="YOUR_INSTANCE_ID",
    token="YOUR_TOKEN",
    client_token="YOUR_CLIENT_TOKEN"
)


@app.post("/webhook")
async def webhook_handler(request: Request):
    """
    Main webhook endpoint that receives messages from Z-API.
    
    Z-API will POST to this endpoint whenever:
    - A message is received
    - A message status changes
    - Other events occur
    """
    # Get the raw JSON payload
    payload = await request.json()
    
    print(f"\n{'='*50}")
    print("Received webhook:")
    print(f"Type: {payload.get('type')}")
    print(f"From: {payload.get('phone')}")
    print(f"{'='*50}\n")
    
    try:
        # Parse webhook into typed message
        message = parse_webhook_message(payload)
        
        # Skip messages sent by us
        if is_from_me(message):
            print("⏭️  Message from me, skipping")
            return JSONResponse({"status": "ok"})
        
        # Skip group messages (optional)
        if is_group_message(message):
            print("👥 Group message, skipping")
            return JSONResponse({"status": "ok"})
        
        # Handle different message types
        await handle_message(message)
        
        return JSONResponse({"status": "ok"})
    
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


async def handle_message(message):
    """
    Handle incoming messages based on their type.
    
    This is where you implement your bot logic.
    """
    sender = message.phone
    
    # Text messages
    if is_text_message(message):
        text_msg: TextMessage = message  # Type narrowing
        print(f"📝 Text from {sender}: {text_msg.message}")
        
        # Echo the message back
        await CLIENT.send_text(
            phone=sender,
            message=f"You said: _{text_msg.message}_"
        )
        
        # Command handling example
        if text_msg.message.lower() == "/help":
            await send_help_message(sender)
        
        elif text_msg.message.lower() == "/status":
            status = await CLIENT.get_status()
            await CLIENT.send_text(
                phone=sender,
                message=f"✅ Connected as: {status.phone}"
            )
    
    # Image messages
    elif is_image_message(message):
        img_msg: ImageMessage = message  # Type narrowing
        print(f"📷 Image from {sender}: {img_msg.image_url}")
        print(f"   Caption: {img_msg.caption}")
        
        await CLIENT.send_text(
            phone=sender,
            message="Nice photo! 📸"
        )
    
    # Audio messages
    elif is_audio_message(message):
        audio_msg = message
        voice_note = "🎤" if audio_msg.ptt else "🎵"
        print(f"{voice_note} Audio from {sender}: {audio_msg.audio_url}")
        
        await CLIENT.send_text(
            phone=sender,
            message="Thanks for the audio!"
        )
    
    # Location messages
    elif is_location_message(message):
        loc_msg = message
        print(f"📍 Location from {sender}: {loc_msg.latitude}, {loc_msg.longitude}")
        
        await CLIENT.send_text(
            phone=sender,
            message=f"Got your location! {loc_msg.name or 'Unknown location'}"
        )
    
    # Default handler for other types
    else:
        print(f"📨 Other message type from {sender}")
        await CLIENT.send_text(
            phone=sender,
            message="Message received! 👍"
        )


async def send_help_message(phone: str):
    """Send help message with available commands."""
    help_text = """
🤖 *Bot Commands*

/help - Show this help message
/status - Check bot status

Just send me a message and I'll echo it back!
    """.strip()
    
    await CLIENT.send_text(phone=phone, message=help_text)


@app.get("/")
async def root():
    """Health check endpoint."""
    status = await CLIENT.get_status()
    return {
        "status": "ok",
        "connected": status.connected,
        "phone": status.phone if status.connected else None
    }


@app.on_event("startup")
async def startup():
    """Check connection on startup."""
    print("\n" + "="*50)
    print("🚀 Z-API Webhook Server Starting...")
    print("="*50)
    
    try:
        status = await CLIENT.get_status()
        if status.connected:
            print(f"✅ Connected as: {status.phone}")
        else:
            print("⚠️  Instance not connected!")
            print("   Please connect your instance first.")
    except Exception as e:
        print(f"❌ Error checking status: {e}")
    
    print("\n💡 Configure Z-API webhook URL to:")
    print("   http://your-server:8000/webhook")
    print("="*50 + "\n")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    print("\n🛑 Shutting down webhook server...")
    await CLIENT.close()
    print("✅ Cleanup complete\n")


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
