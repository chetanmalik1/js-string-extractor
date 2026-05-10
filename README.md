<h1 align="center">JS String Extractor 🕷️</h1>

<p align="center">
  <em>A blazing fast, concurrent JavaScript crawler and secret finder for Bug Bounty Hunters.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Platform-Linux-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Author-Chetan%20Malik-brightgreen.svg" alt="Author">
</p>

---

## 📖 Overview

**JS String Extractor** is a command-line tool built for bug bounty hunters and security researchers. It takes a list of URLs (such as `.js` files extracted via tools like `hakrawler`, `waybackurls`, or `gau`), fetches their contents concurrently, and deeply scans them for sensitive information using customizable Regular Expressions.

Whether you're looking for leaked **AWS Keys, Stripe Tokens, GitHub Secrets**, or highly specific internal **Debug IDs**, JS String Extractor finds them in seconds while presenting the results in a beautiful, hacker-friendly Terminal UI.

## ✨ Features

- **⚡ Blazing Fast:** Built with `aiohttp` and `asyncio` to fetch and scan hundreds of files simultaneously.
- **🎨 Beautiful UI:** Powered by `Rich` for clean progress bars, colorful terminal output, and neat summary tables.
- **🔍 Built-in Patterns:** Comes pre-loaded with regex patterns for common API keys, tokens, and secrets.
- **🛠️ Highly Customizable:** Add custom regex patterns via a JSON file, or interactively enter a custom string right before the scan starts.
- **📁 Structured Output:** Automatically saves all findings along with contextual code snippets into a formatted `results.json` file.

## ⚙️ Installation

1. Clone the repository or download the source code:
   ```bash
   git clone https://github.com/chetanmalik1/js-string-extractor.git
   cd js-string-extractor
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make the script executable (Linux/macOS):
   ```bash
   chmod +x js_string_extractor.py
   ```

## 🚀 Usage

### Basic Scan
Provide a text file containing your target URLs.

```bash
./js_string_extractor.py -f urls.txt
```

### Advanced Options

```bash
./js_string_extractor.py -f urls.txt -o my_custom_results.json -c 100 --custom-regex patterns.json
```

| Flag | Long Flag | Description | Default |
|------|-----------|-------------|---------|
| `-f` | `--file` | Path to the file containing URLs (Required) | `None` |
| `-o` | `--output` | Output JSON file name | `results.json` |
| `-c` | `--concurrency` | Number of concurrent requests to make | `50` |
| | `--custom-regex` | Path to a JSON file containing custom regex patterns | `None` |

### Custom Regex File Format
If you want to use `--custom-regex`, format your JSON file like this:

```json
{
  "My Custom Token": "mycompany_[a-zA-Z0-9]{20}",
  "Internal API Endpoint": "api\\.internal\\.company\\.com/v[1-9]/"
}
```

## 🧠 Built-in Secrets Detection

By default, the tool will automatically look for:
- Google API Keys
- Stripe API Keys (Test & Live)
- GitHub Tokens
- AWS Access Key IDs
- Slack Tokens
- RSA Private Keys
- Generic hardcoded secrets (tokens, passwords, api_keys)

## 👤 Author

Developed by **[Chetan Malik](https://github.com/chetanmalik1)**.

Feel free to contribute, report bugs, or suggest features by opening an issue or a pull request!
