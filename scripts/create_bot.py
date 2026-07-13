#!/usr/bin/env python3
"""Create Bitrix24 bot via VibeCode API."""

import argparse
import json
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def create_bot(api_key: str, bot_name: str, base_url: str = "https://vibecode.bitrix24.tech/v1") -> dict:
    """Create a new bot in Bitrix24.
    
    Args:
        api_key: VibeCode API key
        bot_name: Name for the bot
        base_url: VibeCode API base URL
    
    Returns:
        dict with bot_id and other info
    """
    url = f"{base_url}/bots"
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json",
    }
    body = json.dumps({"name": bot_name}).encode()
    
    req = Request(url, data=body, headers=headers, method="POST")
    
    try:
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            if result.get("success"):
                bot_id = result.get("data", {}).get("id")
                print(f"Bot created successfully!")
                print(f"Bot ID: {bot_id}")
                print(f"Bot Name: {bot_name}")
                return {"bot_id": bot_id, "name": bot_name, "success": True}
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
                return {"success": False, "error": result.get("error")}
    except HTTPError as e:
        error_body = e.read().decode()
        print(f"HTTP Error {e.code}: {error_body}")
        return {"success": False, "error": f"HTTP {e.code}"}
    except URLError as e:
        print(f"Connection error: {e.reason}")
        return {"success": False, "error": str(e.reason)}


def list_bots(api_key: str, base_url: str = "https://vibecode.bitrix24.tech/v1") -> list:
    """List existing bots in Bitrix24."""
    url = f"{base_url}/bots"
    headers = {"X-Api-Key": api_key}
    
    req = Request(url, headers=headers, method="GET")
    
    try:
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            if result.get("success"):
                bots = result.get("data", {}).get("bots", [])
                return bots
            return []
    except Exception as e:
        print(f"Error listing bots: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Create Bitrix24 bot via VibeCode API")
    parser.add_argument("--api-key", required=True, help="VibeCode API key")
    parser.add_argument("--name", required=True, help="Bot name")
    parser.add_argument("--list", action="store_true", help="List existing bots")
    parser.add_argument("--base-url", default="https://vibecode.bitrix24.tech/v1", help="API base URL")
    
    args = parser.parse_args()
    
    if args.list:
        bots = list_bots(args.api_key, args.base_url)
        if bots:
            print("Existing bots:")
            for bot in bots:
                print(f"  - {bot.get('name')} (ID: {bot.get('id')})")
        else:
            print("No bots found.")
        return
    
    result = create_bot(args.api_key, args.name, args.base_url)
    
    if result.get("success"):
        # Save bot info to .env
        bot_id = result["bot_id"]
        env_content = f"""VIBE_API_KEY={args.api_key}
BOT_ID={bot_id}
BOT_NAME={result['name']}
POLL_INTERVAL=3
"""
        print(f"\nAdd to your .env file:")
        print(env_content)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
