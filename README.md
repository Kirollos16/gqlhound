# ⬢ GQLHound - GraphQL Query Hunter

<div align="center">

![GQLHound Logo](gqlhound_logo.png)

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey.svg)

**A powerful static analysis tool to hunt down GraphQL operations hidden in JavaScript files**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Examples](#-examples) • [Contributing](#-contributing)

</div>

---

## 📖 About

GQLHound is a specialized reconnaissance tool designed for bug bounty hunters, penetration testers, and security researchers. It automatically extracts GraphQL queries, mutations, and fragments from JavaScript files, helping you understand the GraphQL API surface of web applications.

### Why GQLHound?

- 🎯 **Accurate Extraction**: Advanced regex patterns catch queries missed by other tools
- 🔍 **Variable Detection**: Automatically identifies query variables and their types
- 🚫 **Smart Deduplication**: Removes duplicate queries using content hashing
- ✅ **Validation**: Filters false positives with GraphQL syntax validation
- 🎨 **Beautiful Output**: Colorized terminal output with proper formatting
- 📁 **File Export**: Save results to file for later analysis
- ⚡ **Progress Tracking**: Visual progress bar for large-scale scans
- 🛠️ **Flexible**: Works with single URLs, HTML pages, or bulk URL lists

---

## ✨ Features

### Core Capabilities
- ✅ Extract GraphQL queries, mutations, fragments, and subscriptions
- ✅ Parse variables with their types (`$id: ID!`, `$name: String`)
- ✅ Handle minified and obfuscated JavaScript
- ✅ Support multiple GraphQL declaration patterns (gql``, graphql(), etc.)
- ✅ Scan HTML pages and automatically analyze all JavaScript files
- ✅ Deduplicate identical queries across multiple files
- ✅ Validate GraphQL syntax to reduce false positives

### Reconnaissance Features
- 🔍 Custom User-Agent support
- 🔍 Custom HTTP headers (Authorization, API keys, etc.)
- 🔍 Configurable request delays (rate limiting)
- 🔍 Adjustable timeout settings
- 🔍 Bulk URL scanning from file
- 🔍 Progress bar for long scans

### Output Options
- 🎨 Colorized terminal output
- 📄 Export to text file
- 📊 Formatted GraphQL with syntax highlighting
- 🏷️ Variable extraction and display

---

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/gqlhound.git
cd gqlhound

# Install dependencies
pip install -r requirements.txt

# Make it executable (Linux/Mac)
chmod +x gqlhound.py

# Run the tool
python gqlhound.py -h
```

### Dependencies
```
requests>=2.31.0
beautifulsoup4>=4.12.0
tqdm>=4.66.0
```

---

## 💻 Usage

### Basic Syntax
```bash
python gqlhound.py [OPTIONS]
```

### Required Arguments (choose one)
| Argument | Description |
|----------|-------------|
| `-u`, `--url` | Single URL to scan (HTML page or JS file) |
| `-l`, `--list` | File containing list of URLs (one per line) |

### Optional Arguments
| Argument | Description | Default |
|----------|-------------|---------|
| `-a`, `--user-agent` | Custom User-Agent string | Mozilla/5.0... |
| `-H`, `--headers` | Custom headers (format: "Key:Value,Key2:Value2") | None |
| `-d`, `--delay` | Delay between requests in seconds | 0 |
| `-t`, `--timeout` | Request timeout in seconds | 10 |
| `-o`, `--output` | Output file to save results | None |
| `--progress` | Show progress bar (for URL lists) | False |

---

## 📚 Examples

### Example 1: Scan a Single Website
```bash
python gqlhound.py -u https://example.com
```

### Example 2: Scan a Specific JavaScript File
```bash
python gqlhound.py -u https://example.com/static/js/app.min.js
```

### Example 3: Bulk Scan from URL List
```bash
# Create a file with URLs (one per line)
cat urls.txt
https://example.com
https://target.com/app.js
https://api.example.com

# Scan all URLs
python gqlhound.py -l urls.txt
```

### Example 4: Scan with Progress Bar and Save Output
```bash
python gqlhound.py -l urls.txt --progress -o results.txt
```

### Example 5: Custom Headers and Delay
```bash
python gqlhound.py -u https://example.com \
  -H "Authorization:Bearer token123,X-API-Key:abc" \
  -d 2 \
  -t 30
```

### Example 6: Authenticated Scanning
```bash
python gqlhound.py -u https://app.example.com \
  -H "Cookie:session=xyz123" \
  -o authenticated_queries.txt
```

### Example 7: Slow Server with Custom Timeout
```bash
python gqlhound.py -u https://slow-site.com -t 60
```

---

## 📊 Sample Output

```
┌───────────────────────────────────────────────────────────────────┐
          GraphQL Operation Scanner v3.0
          Extract GraphQL from JavaScript Files
└───────────────────────────────────────────────────────────────────┘

[*] User-Agent: Mozilla/5.0...
[*] Fetching HTML from: https://example.com
[+] Found 5 JavaScript file(s)

[*] Fetching and analyzing JavaScript file: https://example.com/app.js
[+] Found 3 unique GraphQL operation(s)
================================================================================

[Operation #1]
--------------------------------------------------------------------------------
Variables:
  $userId: ID!
  $limit: Int

```graphql
query GetUserProfile($userId: ID!, $limit: Int) {
  user(id: $userId) {
    id
    name
    email
    posts(limit: $limit) {
      id
      title
      createdAt
    }
  }
}
```
--------------------------------------------------------------------------------

[*] Scan complete!
```

---

## 🎯 Use Cases

### Bug Bounty Hunting
- Discover hidden API endpoints
- Find unauthenticated queries
- Identify sensitive data exposure
- Map GraphQL schema

### Penetration Testing
- Enumerate GraphQL operations
- Identify input validation points
- Test for authorization bypasses
- Analyze query complexity

### Security Research
- Study GraphQL implementations
- Compare client vs server schemas
- Find deprecated fields
- Discover introspection queries

---

## 🛡️ Best Practices

1. **Always get authorization** before scanning third-party websites
2. **Use rate limiting** (`-d` flag) to avoid overwhelming servers
3. **Save output** (`-o` flag) for large scans to avoid losing data
4. **Use custom User-Agent** to identify your scans in server logs
5. **Respect robots.txt** and website terms of service

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Ideas for Contributions
- Add support for async/concurrent requests
- Implement GraphQL introspection query detection
- Add JSON output format
- Create Docker container
- Add more extraction patterns
- Improve variable type detection

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is intended for legal security research and authorized testing only. Users are responsible for complying with applicable laws and regulations. The authors assume no liability for misuse or damage caused by this tool.

---

## 🙏 Acknowledgments

- Inspired by the need for better GraphQL reconnaissance tools
- Thanks to the bug bounty and security research community
- Built with ❤️ for security researchers

---

## 📬 Contact

- **Author**: Arion
- **GitHub**: [@yourusername](https://github.com/yourusername)
- **Issues**: [Report a bug](https://github.com/yourusername/gqlhound/issues)

---

<div align="center">

**If you found this tool helpful, please give it a ⭐️!**

Made with ⬢ by security researchers, for security researchers

</div>
