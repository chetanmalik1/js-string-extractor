#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JS String Extractor - A Bug Bounty Tool
Author: Chetan Malik

This tool takes a file containing URLs (e.g., from hakrawler), filters for target files (like .js),
concurrently fetches their content, and searches for predefined or custom secrets/strings (API keys, debug IDs, etc.).
"""

import asyncio
import aiohttp
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

# Built-in regex patterns for common secrets/API keys
BUILTIN_PATTERNS = {
    "Google API Key": r"AIza[0-9A-Za-z-_]{35}",
    "Stripe API Key": r"(?:sk|pk)_(?:test|live)_[0-9a-zA-Z]{24}",
    "GitHub Token": r"(?:ghp|gho|ghu|ghs|ghr)_[0-9a-zA-Z]{36}",
    "AWS Access Key ID": r"AKIA[0-9A-Z]{16}",
    "Slack Token": r"xox[baprs]-[0-9]{12}-[0-9]{12}-[0-9a-zA-Z]{24}",
    "RSA Private Key": r"-----BEGIN RSA PRIVATE KEY-----",
    "Generic Secret": r"(?i)(?:secret|token|api_key|password)[\s=:]+['\"]([a-zA-Z0-9_\-\.]{15,})['\"]"
}

def print_banner():
    banner = """[bold green]
      _  _____   _____ _        _             ______      _                  _             
     | |/ ____| / ____| |      (_)           |  ____|    | |                | |            
     | | (___  | (___ | |_ _ __ _ _ __   __ _| |__  __  _| |_ _ __ __ _  ___| |_ ___  _ __ 
 _   | |\___ \  \___ \| __| '__| | '_ \ / _` |  __| \ \/ / __| '__/ _` |/ __| __/ _ \| '__|
| |__| |____) | ____) | |_| |  | | | | | (_| | |____ >  <| |_| | | (_| | (__| || (_) | |   
 \____/|_____/ |_____/ \__|_|  |_|_| |_|\__, |______/_/\_\\__|_|  \__,_|\___|\__\___/|_|   
                                         __/ |                                             
                                        |___/                                              
[/bold green]
[bold cyan]Author:[/bold cyan] Chetan Malik
[bold yellow]Description:[/bold yellow] Concurrent JS Crawler & Secret Finder for Bug Bounty Hunters
"""
    console.print(Panel(banner, expand=False))

def setup_args():
    parser = argparse.ArgumentParser(description="JS String Extractor by Chetan Malik")
    parser.add_argument("-f", "--file", required=True, help="Path to the file containing URLs (e.g., hakrawler output)")
    parser.add_argument("-o", "--output", default="results.json", help="Output JSON file name (default: results.json)")
    parser.add_argument("-c", "--concurrency", type=int, default=50, help="Number of concurrent requests (default: 50)")
    parser.add_argument("--custom-regex", help="Path to a JSON file containing custom generic regex patterns")
    
    return parser.parse_args()

def load_urls(filepath):
    """Load URLs from file and filter roughly by HTTP/HTTPS."""
    urls = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("http://") or line.startswith("https://"):
                    urls.append(line)
        return urls
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] File '{filepath}' not found.")
        sys.exit(1)

def interactive_setup(patterns):
    """Ask user if they want to add custom strings before crawling."""
    console.print("\n[bold cyan][*] Configuration[/bold cyan]")
    
    add_custom = Confirm.ask("Do you want to search for a specific custom string? (Exact match)")
    if add_custom:
        custom_string = Prompt.ask("Enter the custom string to search for")
        if custom_string:
            patterns[f"Custom String ({custom_string})"] = re.escape(custom_string)
            
    return patterns

async def fetch_and_scan(session, url, patterns, results, semaphore, progress, task_id):
    """Fetch URL content and scan for patterns."""
    async with semaphore:
        try:
            async with session.get(url, timeout=10, ssl=False) as response:
                content = await response.text()
                
                found_items = []
                for name, pattern in patterns.items():
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        # Extract context (e.g., 20 chars before and after)
                        start = max(0, match.start() - 20)
                        end = min(len(content), match.end() + 20)
                        context = content[start:end].replace('\n', ' ').strip()
                        
                        found_items.append({
                            "type": name,
                            "match": match.group(0),
                            "context": context
                        })
                
                if found_items:
                    results[url] = found_items
                    
        except Exception as e:
            # We silently ignore connection errors to avoid spamming the console
            pass
        finally:
            progress.advance(task_id)

async def main():
    print_banner()
    args = setup_args()
    
    # 1. Load URLs
    urls = load_urls(args.file)
    if not urls:
        console.print("[bold red][!] No valid URLs found in the file.[/bold red]")
        sys.exit(1)
        
    console.print(f"[green][+][/green] Loaded [bold]{len(urls)}[/bold] URLs from {args.file}")
    
    # 2. Setup Patterns
    patterns = BUILTIN_PATTERNS.copy()
    if args.custom_regex:
        try:
            with open(args.custom_regex, "r") as f:
                custom_dict = json.load(f)
                patterns.update(custom_dict)
            console.print(f"[green][+][/green] Loaded custom patterns from {args.custom_regex}")
        except Exception as e:
            console.print(f"[bold red][!] Error loading custom regex file:[/bold red] {e}")

    patterns = interactive_setup(patterns)
    
    # Compile regexes for speed
    compiled_patterns = {name: re.compile(pat) for name, pat in patterns.items()}
    
    # 3. Crawl & Scan
    results = {}
    semaphore = asyncio.Semaphore(args.concurrency)
    
    console.print("\n[bold cyan][*] Starting concurrent scan...[/bold cyan]")
    
    connector = aiohttp.TCPConnector(limit_per_host=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            scan_task = progress.add_task("[cyan]Scanning URLs...", total=len(urls))
            
            tasks = [
                fetch_and_scan(session, url, compiled_patterns, results, semaphore, progress, scan_task)
                for url in urls
            ]
            
            await asyncio.gather(*tasks)

    # 4. Process and Save Results
    if results:
        console.print(f"\n[bold green][+] Scan complete! Found secrets in {len(results)} files.[/bold green]")
        
        # Save to JSON
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
        console.print(f"[green][+][/green] Results successfully saved to [bold]{args.output}[/bold]")
        
        # Display a summary table
        table = Table(title="Finding Summary", show_header=True, header_style="bold magenta")
        table.add_column("URL", style="cyan", overflow="fold")
        table.add_column("Finding Type", style="yellow")
        table.add_column("Count", style="green", justify="right")
        
        for url, items in results.items():
            types_count = {}
            for item in items:
                types_count[item['type']] = types_count.get(item['type'], 0) + 1
                
            for v_type, count in types_count.items():
                table.add_row(url, v_type, str(count))
                
        console.print(table)
    else:
        console.print("\n[bold yellow][-] Scan complete. No secrets or requested strings were found.[/bold yellow]")

if __name__ == "__main__":
    # Prevent RuntimeError for Windows users using asyncio, though this is primarily for Linux
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold red][!] Scan aborted by user.[/bold red]")
        sys.exit(0)
