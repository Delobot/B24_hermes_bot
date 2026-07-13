#!/usr/bin/env python3
"""Setup B24_hermes_bot configuration by reading from Hermes profile."""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime


HERMES_HOME = Path.home() / ".hermes"
HERMES_PROFILES = [
    HERMES_HOME / "profiles" / "default" / ".env",
    HERMES_HOME / ".env",
]

# B24_hermes_bot variables to add
BOT_VARS = {
    "VIBE_API_KEY": "",
    "BOT_ID": "19",
    "BOT_NAME": "hermes-bot",
    "POLL_INTERVAL": "3",
    "HERMES_MODEL": "",
}


def find_hermes_env():
    """Find the Hermes .env file."""
    for path in HERMES_PROFILES:
        if path.exists():
            return path
    return None


def read_hermes_env(env_path):
    """Read key=value pairs from a .env file."""
    config = {}
    if not env_path or not env_path.exists():
        return config
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            config[key.strip()] = value.strip().strip('"').strip("'")
    return config


def backup_env(env_path):
    """Create a timestamped backup of the .env file."""
    if not env_path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = env_path.with_suffix(f".bak.{ts}")
    shutil.copy2(env_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path


def merge_env(env_path, new_vars):
    """Merge new variables into existing .env, preserving existing values."""
    existing = read_hermes_env(env_path)

    lines = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    # Find keys already in file
    existing_keys = set()
    for line in lines:
        line_s = line.strip()
        if line_s and not line_s.startswith("#") and "=" in line_s:
            key = line_s.partition("=")[0].strip()
            existing_keys.add(key)

    # Append missing keys
    appended = []
    for key, default in new_vars.items():
        if key not in existing_keys:
            val = existing.get(key, default)
            lines.append(f"{key}={val}")
            appended.append(key)

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return appended


def write_env_interactive(env_path):
    """Write a fresh .env file with prompted values."""
    print("\nEnter configuration values (press Enter for defaults):\n")

    values = {}
    for key, default in BOT_VARS.items():
        prompt = f"  {key}"
        if default:
            prompt += f" [{default}]"
        prompt += ": "
        user_input = input(prompt).strip()
        values[key] = user_input if user_input else default

    lines = [f"{k}={v}" for k, v in values.items()]
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return values


def detect_install_mode():
    """Detect whether running in Docker or venv."""
    # Check if inside a Docker container
    if Path("/.dockerenv").exists() or os.environ.get("DOCKER_CONTAINER"):
        return "docker"

    # Check for docker-compose.yml in project root
    project_root = Path(__file__).resolve().parent.parent
    if (project_root / "docker-compose.yml").exists():
        # Check if docker is available
        if shutil.which("docker"):
            return "docker"

    # Check for venv
    if os.environ.get("VIRTUAL_ENV") or (Path(__file__).resolve().parent.parent / "venv").exists():
        return "venv"

    return "venv"  # default


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Setup B24_hermes_bot .env configuration")
    parser.add_argument("--env-path", type=Path, help="Target .env file path (default: project root .env)")
    parser.add_argument("--interactive", action="store_true", help="Prompt for all values")
    parser.add_argument("--vibe-key", help="VIBE_API_KEY value")
    parser.add_argument("--bot-id", help="BOT_ID value")
    parser.add_argument("--bot-name", help="BOT_NAME value")
    parser.add_argument("--poll-interval", help="POLL_INTERVAL value")
    parser.add_argument("--hermes-model", help="HERMES_MODEL value")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    env_path = args.env_path or (project_root / ".env")

    # Step 1: Check Hermes installation
    print("Checking Hermes installation...")
    if not HERMES_HOME.exists():
        print(f"  Hermes home not found at {HERMES_HOME}")
        print("  Continuing with defaults (no HERMES_MODEL will be read).")
    else:
        print(f"  Found Hermes home: {HERMES_HOME}")

    # Step 2: Find and read Hermes .env
    hermes_env_path = find_hermes_env()
    hermes_config = {}
    if hermes_env_path:
        print(f"  Found Hermes config: {hermes_env_path}")
        hermes_config = read_hermes_env(hermes_env_path)
        if "HERMES_MODEL" in hermes_config:
            print(f"  HERMES_MODEL={hermes_config['HERMES_MODEL']}")
        else:
            print("  HERMES_MODEL not found in Hermes config.")
    else:
        print("  No Hermes .env file found.")

    # Step 3: Backup existing .env
    if env_path.exists():
        print(f"\nBacking up existing .env...")
        backup_env(env_path)

    # Step 4: Write or merge .env
    if args.interactive:
        print(f"\nWriting .env to: {env_path}")
        values = write_env_interactive(env_path)
        print(f"\nConfiguration written to {env_path}")
        for k, v in values.items():
            print(f"  {k}={v}")
    else:
        # Build vars from CLI args, falling back to Hermes config, then defaults
        merged = dict(BOT_VARS)

        # Hermes model from profile
        if hermes_config.get("HERMES_MODEL"):
            merged["HERMES_MODEL"] = hermes_config["HERMES_MODEL"]

        # CLI overrides
        if args.vibe_key:
            merged["VIBE_API_KEY"] = args.vibe_key
        if args.bot_id:
            merged["BOT_ID"] = args.bot_id
        if args.bot_name:
            merged["BOT_NAME"] = args.bot_name
        if args.poll_interval:
            merged["POLL_INTERVAL"] = args.poll_interval
        if args.hermes_model:
            merged["HERMES_MODEL"] = args.hermes_model

        if env_path.exists():
            appended = merge_env(env_path, merged)
            if appended:
                print(f"\nAdded new variables to {env_path}: {', '.join(appended)}")
            else:
                print(f"\nAll variables already present in {env_path}.")
        else:
            lines = [f"{k}={v}" for k, v in merged.items()]
            env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(f"\nCreated {env_path}")

    # Step 5: Detect and report install mode
    mode = detect_install_mode()
    print(f"\nDetected install mode: {mode}")
    if mode == "docker":
        print("  Start with: docker compose up -d")
    else:
        print("  Start with: python bot_handler.py")

    print("\nSetup complete!")


if __name__ == "__main__":
    main()
