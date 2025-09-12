#!/usr/bin/env python3
"""Steam Shelf CLI - Manage non-Steam games in your Steam library."""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

import steamclient
from core.models.repository import NonSteamGameRepository
from core.services.steam_db_utils import SteamDatabase
from core.utils.vdf_utils import parse_vdf


def kill_steam():
    """Forcefully terminate Steam process."""
    try:
        subprocess.run(["taskkill", "/IM", "Steam.exe", "/F"], 
                      capture_output=True, check=False)
        print("Steam process terminated.")
    except Exception as e:
        print(f"Warning: Could not kill Steam process: {e}")


def get_main_user() -> steamclient.User:
    """Get the primary Steam user."""
    users = steamclient.get_users()
    if not users:
        print("Error: No Steam users found.")
        sys.exit(1)
    return users[0]


def discover_games(args):
    """Discover and add games from a directory."""
    games_path = Path(args.directory)
    
    if not games_path.exists():
        print(f"Error: Directory '{games_path}' does not exist.")
        sys.exit(1)
    
    # Get user
    user = get_main_user()
    print(f"Using Steam user: {user.persona_name} (ID: {user.id})")
    
    # Create repository
    repo = NonSteamGameRepository(user_id=user.id)
    
    # Load existing shortcuts if they exist
    shortcuts_path = Path(f"{steamclient.STEAM_PATH}\\userdata\\{user.id}\\config\\shortcuts.vdf")
    if shortcuts_path.exists() and not args.fresh:
        print("Loading existing shortcuts...")
        repo.load_games_from_vdf(shortcuts_path)
        print(f"Loaded {len(repo.games)} existing games.")
    
    print(f"Discovering games in: {games_path}")
    repo.load_games_from_directory(games_path)
    
    if not repo.games:
        print("No games found.")
        return
    
    # Show found games
    print(f"\nFound {len(repo.games)} games:")
    for i, game in enumerate(repo.games, 1):
        print(f"{i:2d}. {game.AppName}")
    
    # Confirm installation
    if not args.yes:
        while True:
            ans = input("\nAdd these games to Steam? (Y/n): ").lower().strip()
            if ans in ("y", "yes", ""):
                break
            elif ans in ("n", "no"):
                print("Operation cancelled.")
                return
            print("Please enter 'y' or 'n'")
    
    # Kill Steam if requested
    if args.kill_steam:
        kill_steam()
    
    # Save games
    print("Saving games to shortcuts.vdf...")
    repo.save_games_as_vdf(shortcuts_path)
    
    # Download images if requested
    if not args.no_images:
        print("Downloading game artwork...")
        try:
            repo.save_game_images()
            print("Artwork downloaded successfully.")
        except Exception as e:
            print(f"Warning: Could not download some artwork: {e}")
    
    print(f"Successfully added {len(repo.games)} games to Steam!")


def list_games(args):
    """List games currently in Steam shortcuts."""
    user = get_main_user()
    shortcuts_path = Path(f"{steamclient.STEAM_PATH}\\userdata\\{user.id}\\config\\shortcuts.vdf")
    
    if not shortcuts_path.exists():
        print("No shortcuts.vdf file found. No non-Steam games installed.")
        return
    
    repo = NonSteamGameRepository(user_id=user.id)
    repo.load_games_from_vdf(shortcuts_path)
    
    if not repo.games:
        print("No non-Steam games found in shortcuts.vdf")
        return
    
    print(f"Found {len(repo.games)} non-Steam games:")
    for i, game in enumerate(repo.games, 1):
        print(f"{i:2d}. {game.AppName}")
        if args.verbose:
            print(f"    Steam ID: {game.appid}")
            print(f"    Executable: {game.Exe}")
            print(f"    Directory: {game.StartDir}")
            print()


def sync_database(args):
    """Sync the local Steam game database."""
    print("Syncing Steam game database...")
    db = SteamDatabase()
    db.sync()
    print("Database sync completed.")


def clear_games(args):
    """Clear all non-Steam games from shortcuts."""
    user = get_main_user()
    shortcuts_path = Path(f"{steamclient.STEAM_PATH}\\userdata\\{user.id}\\config\\shortcuts.vdf")
    
    if not shortcuts_path.exists():
        print("No shortcuts.vdf file found.")
        return
    
    if not args.yes:
        ans = input("Are you sure you want to remove ALL non-Steam games? (y/N): ").lower().strip()
        if ans not in ("y", "yes"):
            print("Operation cancelled.")
            return
    
    # Kill Steam if requested
    if args.kill_steam:
        kill_steam()
    
    # Create empty repository and save
    repo = NonSteamGameRepository(user_id=user.id)
    repo.games = []
    repo.save_games_as_vdf(shortcuts_path)
    
    print("All non-Steam games removed from Steam.")


def read_vdf(args):
    """Read and display contents of a VDF file."""
    vdf_path = Path(args.file)
    
    # Special case: if user specifies "shortcuts", find their shortcuts.vdf
    if args.file.lower() == "shortcuts":
        user = get_main_user()
        vdf_path = Path(f"{steamclient.STEAM_PATH}\\userdata\\{user.id}\\config\\shortcuts.vdf")
        print(f"Reading shortcuts.vdf for user {user.persona_name}: {vdf_path}")
    
    if not vdf_path.exists():
        print(f"Error: VDF file '{vdf_path}' does not exist.")
        sys.exit(1)
    
    try:
        print(f"Reading VDF file: {vdf_path}")
        vdf_data = parse_vdf(vdf_path)
        
        if args.format == 'json':
            # Pretty print as JSON
            print(json.dumps(vdf_data, indent=2, ensure_ascii=False))
        
        elif args.format == 'shortcuts':
            # Display as formatted shortcuts list
            shortcuts = vdf_data.get("shortcuts", {})
            if not shortcuts:
                print("No shortcuts found in VDF file.")
                return
            
            print(f"\nFound {len(shortcuts)} shortcuts:")
            print("-" * 60)
            
            for idx, (key, shortcut) in enumerate(shortcuts.items(), 1):
                print(f"{idx:2d}. {shortcut.get('AppName', 'Unknown Game')}")
                if args.verbose:
                    print(f"    App ID: {shortcut.get('appid', 'N/A')}")
                    print(f"    Executable: {shortcut.get('Exe', 'N/A')}")
                    print(f"    Start Dir: {shortcut.get('StartDir', 'N/A')}")
                    print(f"    Hidden: {'Yes' if shortcut.get('IsHidden', 0) else 'No'}")
                    print(f"    Launch Options: {shortcut.get('LaunchOptions', 'None')}")
                    if shortcut.get('tags'):
                        print(f"    Tags: {shortcut.get('tags')}")
                    print()
        
        elif args.format == 'summary':
            # Display summary information
            print("\nVDF File Summary:")
            print(f"File size: {vdf_path.stat().st_size} bytes")
            
            def count_items(data, level=0):
                """Recursively count items in VDF data."""
                total = 0
                for key, value in data.items():
                    total += 1
                    if isinstance(value, dict):
                        total += count_items(value, level + 1)
                return total
            
            total_items = count_items(vdf_data)
            print(f"Total items: {total_items}")
            
            # Show top-level keys
            print(f"Top-level sections: {list(vdf_data.keys())}")
            
            # Show shortcuts summary if present
            if "shortcuts" in vdf_data:
                shortcuts = vdf_data["shortcuts"]
                print(f"Number of shortcuts: {len(shortcuts)}")
                
                # Count by type or other attributes
                hidden_count = sum(1 for s in shortcuts.values() 
                                 if isinstance(s, dict) and s.get('IsHidden', 0))
                print(f"Hidden shortcuts: {hidden_count}")
        
        else:
            # Raw format - just show the structure
            def print_structure(data, indent=0):
                """Print the structure of VDF data."""
                for key, value in data.items():
                    spaces = "  " * indent
                    if isinstance(value, dict):
                        print(f"{spaces}{key}/ ({len(value)} items)")
                        if indent < 2:  # Limit depth for readability
                            print_structure(value, indent + 1)
                    else:
                        value_str = str(value)
                        if len(value_str) > 50:
                            value_str = value_str[:47] + "..."
                        print(f"{spaces}{key}: {value_str}")
            
            print("\nVDF Structure:")
            print_structure(vdf_data)
    
    except Exception as e:
        print(f"Error reading VDF file: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Steam Shelf - Manage non-Steam games in your Steam library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s discover "C:/Games" --kill-steam
  %(prog)s list --verbose
  %(prog)s sync-db
  %(prog)s clear --yes
  %(prog)s read-vdf shortcuts.vdf --format json
  %(prog)s read-vdf shortcuts.vdf --format shortcuts --verbose
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover and add games from directory')
    discover_parser.add_argument('directory', help='Directory to scan for games')
    discover_parser.add_argument('--kill-steam', action='store_true', 
                                help='Kill Steam process before saving')
    discover_parser.add_argument('--no-images', action='store_true',
                                help='Skip downloading game artwork')
    discover_parser.add_argument('--fresh', action='store_true',
                                help='Start fresh (ignore existing shortcuts)')
    discover_parser.add_argument('-y', '--yes', action='store_true',
                                help='Skip confirmation prompt')
    discover_parser.set_defaults(func=discover_games)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List current non-Steam games')
    list_parser.add_argument('-v', '--verbose', action='store_true',
                           help='Show detailed game information')
    list_parser.set_defaults(func=list_games)
    
    # Sync database command
    sync_parser = subparsers.add_parser('sync-db', help='Sync Steam game database')
    sync_parser.set_defaults(func=sync_database)
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Remove all non-Steam games')
    clear_parser.add_argument('--kill-steam', action='store_true',
                             help='Kill Steam process before clearing')
    clear_parser.add_argument('-y', '--yes', action='store_true',
                             help='Skip confirmation prompt')
    clear_parser.set_defaults(func=clear_games)
    
    # Read VDF command
    read_parser = subparsers.add_parser('read-vdf', help='Read and display VDF file contents')
    read_parser.add_argument('file', help='Path to VDF file (use "shortcuts" for current user shortcuts.vdf)')
    read_parser.add_argument('--format', choices=['json', 'shortcuts', 'summary', 'raw'], 
                           default='shortcuts', help='Output format (default: shortcuts)')
    read_parser.add_argument('-v', '--verbose', action='store_true',
                           help='Show detailed information')
    read_parser.set_defaults(func=read_vdf)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
