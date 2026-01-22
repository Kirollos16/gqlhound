import re
import os
import sys
import time
import argparse
import hashlib
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Color definitions (ANSI escape codes)
class Colors:
    RED = '\033[38;2;255;82;82m'
    GREEN = '\033[38;2;0;230;118m'
    BLUE = '\033[38;2;41;121;255m'
    YELLOW = '\033[38;2;255;255;0m'
    ORANGE = '\033[38;2;255;152;0m'
    PURPLE = '\033[38;2;170;0;255m'
    CYAN = '\033[38;2;0;229;255m'
    PINK = '\033[38;2;255;64;129m'
    LT_GRAY = '\033[38;2;189;189;189m'
    DK_GRAY = '\033[38;2;66;66;66m'
    BLACK = '\033[38;2;0;0;0m'
    WHITE = '\033[38;2;255;255;255m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def extract_gql_from_js(content):
    """
    Extract GraphQL operations from JavaScript content with enhanced patterns.
    """
    patterns = [
        # Standard GraphQL operations with nested braces support
        r'(?P<operation>query|mutation|fragment)\s+[\w]*\s*(?:\([^)]*\))?\s*\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}',
        
        # Template literals (gql`...`)
        r'gql`([^`]*)`',
        
        # String literals with graphql function
        r'graphql\s*\(\s*["\']([^"\']+)["\']\s*\)',
        
        # JSON encoded queries
        r'["\']query["\']:\s*["\']([^"\']+)["\']',
        
        # operationName patterns
        r'operationName\s*:\s*["\']([^"\']+)["\']',
    ]

    found = []
    for pattern in patterns:
        try:
            matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
            for m in matches:
                query_text = m.group(0)
                found.append(query_text)
        except Exception as e:
            # Continue processing other patterns even if one fails
            continue
    
    return found

def is_valid_graphql(query_string):
    """
    Validate if the extracted string is likely a valid GraphQL query.
    """
    # Check for required GraphQL keywords
    if not re.search(r'\b(query|mutation|fragment|subscription)\b', query_string, re.IGNORECASE):
        return False
    
    # Check for balanced braces
    open_braces = query_string.count('{')
    close_braces = query_string.count('}')
    
    if open_braces != close_braces or open_braces == 0:
        return False
    
    # Check minimum length (avoid false positives)
    if len(query_string.strip()) < 10:
        return False
    
    return True

def extract_variables(graphql_string):
    """
    Extract variables and their types from GraphQL query.
    """
    var_pattern = r'\$(\w+)\s*:\s*([^\s,\)!]+!?)'
    variables = re.findall(var_pattern, graphql_string)
    return variables

def clean_graphql_query(graphql_string):
    """
    Clean and format GraphQL query with proper indentation.
    """
    # Remove template literal markers and function wrappers
    cleaned = re.sub(r'(gql`|`|graphql\s*\(|^\)|["\'](query|mutation)["\']:\s*["\']|["\']$)', '', graphql_string)
    
    # Remove excessive whitespace but preserve structure
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
    
    # Format with proper indentation
    result = []
    indent_level = 0
    i = 0
    
    while i < len(cleaned):
        char = cleaned[i]
        
        if char == '{':
            result.append(' {\n')
            indent_level += 1
            result.append('  ' * indent_level)
        elif char == '}':
            indent_level -= 1
            result.append('\n' + '  ' * indent_level + '}')
        elif char == ',':
            result.append(',\n' + '  ' * indent_level)
        elif char == '\n':
            result.append('\n' + '  ' * indent_level)
        else:
            result.append(char)
        
        i += 1
    
    formatted = ''.join(result).strip()
    
    # Clean up extra spaces
    formatted = re.sub(r' +', ' ', formatted)
    formatted = re.sub(r'\n +\n', '\n', formatted)
    
    return formatted

def format_graphql_output(graphql_string):
    """
    Format GraphQL string with proper indentation and markdown code block.
    """
    cleaned = clean_graphql_query(graphql_string)
    
    output = "```graphql\n"
    output += cleaned + "\n"
    output += "```"
    
    return output

def deduplicate_operations(operations):
    """
    Remove duplicate GraphQL operations based on content hash.
    """
    unique_ops = {}
    
    for op in operations:
        # Normalize operation for hashing (remove whitespace differences)
        normalized = re.sub(r'\s+', '', op)
        op_hash = hashlib.md5(normalized.encode()).hexdigest()
        
        if op_hash not in unique_ops:
            unique_ops[op_hash] = op
    
    return list(unique_ops.values())

def analyze_js_file(js_url, headers, delay=0, timeout=10, output_file=None):
    """
    Fetch and analyze a JavaScript file URL for GraphQL operations.
    """
    print(f"\n{Colors.CYAN}[*]{Colors.RESET} Fetching and analyzing JavaScript file: {Colors.BLUE}{js_url}{Colors.RESET}")
    
    if delay > 0:
        print(f"{Colors.YELLOW}[*]{Colors.RESET} Waiting {delay} seconds before request...")
        time.sleep(delay)
    
    try:
        response = requests.get(js_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        js_content = response.text
        
        # Extract operations
        ops = extract_gql_from_js(js_content)
        
        # Validate operations
        ops = [op for op in ops if is_valid_graphql(op)]
        
        # Deduplicate
        ops = deduplicate_operations(ops)
        
        if ops:
            print(f"{Colors.GREEN}[+]{Colors.RESET} Found {Colors.BOLD}{len(ops)}{Colors.RESET} unique GraphQL operation(s) in {Colors.BLUE}{js_url}{Colors.RESET}")
            print("=" * 80)
            
            file_output = []
            
            for idx, op in enumerate(ops, 1):
                print(f"\n{Colors.ORANGE}[Operation #{idx}]{Colors.RESET}")
                print("-" * 80)
                
                # Extract and display variables
                variables = extract_variables(op)
                if variables:
                    print(f"{Colors.CYAN}Variables:{Colors.RESET}")
                    for var_name, var_type in variables:
                        print(f"  {Colors.PURPLE}${var_name}{Colors.RESET}: {Colors.YELLOW}{var_type}{Colors.RESET}")
                    print()
                
                formatted_op = format_graphql_output(op)
                print(formatted_op)
                print("-" * 80)
                
                # Collect for file output
                if output_file:
                    file_output.append(f"\n[Operation #{idx}]\n")
                    file_output.append(f"URL: {js_url}\n")
                    if variables:
                        file_output.append(f"Variables:\n")
                        for var_name, var_type in variables:
                            file_output.append(f"  ${var_name}: {var_type}\n")
                    file_output.append(f"\n{formatted_op}\n")
                    file_output.append("-" * 80 + "\n")
            
            # Write to output file if specified
            if output_file and file_output:
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.writelines(file_output)
        else:
            print(f"{Colors.YELLOW}[-]{Colors.RESET} No GraphQL operations found in {Colors.BLUE}{js_url}{Colors.RESET}")
            
    except requests.exceptions.Timeout:
        print(f"{Colors.RED}[!]{Colors.RESET} Timeout error fetching {js_url} (exceeded {timeout}s)")
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}[!]{Colors.RESET} Error fetching {js_url}: {e}")
    except Exception as e:
        print(f"{Colors.RED}[!]{Colors.RESET} Unexpected error processing {js_url}: {e}")

def scan_url(url, headers, delay=0, timeout=10, output_file=None):
    """
    Fetch an HTML page, extract JavaScript file URLs, and analyze them.
    """
    print(f"\n{Colors.CYAN}[*]{Colors.RESET} Fetching HTML from: {Colors.BLUE}{url}{Colors.RESET}")
    
    if delay > 0:
        print(f"{Colors.YELLOW}[*]{Colors.RESET} Waiting {delay} seconds before request...")
        time.sleep(delay)
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <script src="...">
        scripts = [script.get('src') for script in soup.find_all('script') if script.get('src')]

        if not scripts:
            print(f"{Colors.YELLOW}[-]{Colors.RESET} No external JavaScript files found in {url}")
            return

        print(f"{Colors.GREEN}[+]{Colors.RESET} Found {Colors.BOLD}{len(scripts)}{Colors.RESET} JavaScript file(s)")
        
        for script_src in scripts:
            if not script_src.startswith('http'):
                script_url = requests.compat.urljoin(url, script_src)
            else:
                script_url = script_src

            analyze_js_file(script_url, headers, delay, timeout, output_file)

    except requests.exceptions.Timeout:
        print(f"{Colors.RED}[!]{Colors.RESET} Timeout error fetching {url} (exceeded {timeout}s)")
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}[!]{Colors.RESET} Error fetching {url}: {e}")
    except Exception as e:
        print(f"{Colors.RED}[!]{Colors.RESET} Unexpected error processing {url}: {e}")

def process_url_list(file_path, headers, delay=0, timeout=10, output_file=None, show_progress=True):
    """
    Process a list of URLs from a file.
    """
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        print(f"{Colors.CYAN}[*]{Colors.RESET} Loaded {Colors.BOLD}{len(urls)}{Colors.RESET} URL(s) from {Colors.BLUE}{file_path}{Colors.RESET}")
        
        # Use tqdm for progress bar if requested
        url_iterator = tqdm(enumerate(urls, 1), total=len(urls), desc="Processing URLs") if show_progress else enumerate(urls, 1)
        
        for idx, url in url_iterator:
            if not show_progress:
                print(f"\n{'='*80}")
                print(f"{Colors.CYAN}[*]{Colors.RESET} Processing URL {Colors.BOLD}{idx}/{len(urls)}{Colors.RESET}: {Colors.BLUE}{url}{Colors.RESET}")
                print(f"{'='*80}")
            
            if url.lower().endswith('.js'):
                analyze_js_file(url, headers, delay, timeout, output_file)
            else:
                scan_url(url, headers, delay, timeout, output_file)
                
    except FileNotFoundError:
        print(f"{Colors.RED}[!]{Colors.RESET} Error: File '{file_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}[!]{Colors.RESET} Error reading file: {e}")
        sys.exit(1)

def parse_custom_headers(header_string):
    """
    Parse custom headers from string format: "Header1:Value1,Header2:Value2"
    """
    headers = {}
    if header_string:
        pairs = header_string.split(',')
        for pair in pairs:
            if ':' in pair:
                key, value = pair.split(':', 1)
                headers[key.strip()] = value.strip()
    return headers

def main():
    banner = f"""
{Colors.LT_GRAY}┌───────────────────────────────────────────────────────────────────┐{Colors.RESET}
{Colors.CYAN}{Colors.BOLD}          GraphQL Operation Scanner {Colors.RESET}
{Colors.WHITE}          Extract GraphQL from JavaScript Files{Colors.RESET}
{Colors.LT_GRAY}└───────────────────────────────────────────────────────────────────┘{Colors.RESET}
    """
    print(banner)
    
    parser = argparse.ArgumentParser(
        description='Scan URLs or JavaScript files for GraphQL operations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a single URL
  python app.py -u https://example.com
  
  # Scan a JavaScript file directly
  python app.py -u https://example.com/app.js
  
  # Scan multiple URLs from a file with progress bar
  python app.py -l urls.txt --progress
  
  # Save results to file
  python app.py -l urls.txt -o results.txt
  
  # Custom user agent, delay, and timeout
  python app.py -u https://example.com -a "CustomBot/1.0" -d 2 -t 30
  
  # Custom headers
  python app.py -u https://example.com -H "Authorization:Bearer token,X-API-Key:12345"
        """
    )
    
    # URL input options
    url_group = parser.add_mutually_exclusive_group(required=True)
    url_group.add_argument('-u', '--url', help='Single URL to scan (HTML page or JS file)')
    url_group.add_argument('-l', '--list', help='File containing list of URLs (one per line)')
    
    # Optional arguments
    parser.add_argument('-a', '--user-agent', default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                       help='Custom User-Agent string')
    parser.add_argument('-H', '--headers', help='Custom headers (format: "Header1:Value1,Header2:Value2")')
    parser.add_argument('-d', '--delay', type=int, default=0,
                       help='Delay between requests in seconds (default: 0)')
    parser.add_argument('-t', '--timeout', type=int, default=10,
                       help='Request timeout in seconds (default: 10)')
    parser.add_argument('-o', '--output', help='Output file to save results (optional)')
    parser.add_argument('--progress', action='store_true',
                       help='Show progress bar when processing multiple URLs')
    
    args = parser.parse_args()
    
    # Build headers
    headers = {"User-Agent": args.user_agent}
    
    # Add custom headers if provided
    if args.headers:
        custom_headers = parse_custom_headers(args.headers)
        headers.update(custom_headers)
    
    print(f"{Colors.CYAN}[*]{Colors.RESET} User-Agent: {Colors.GREEN}{headers['User-Agent']}{Colors.RESET}")
    if args.delay > 0:
        print(f"{Colors.CYAN}[*]{Colors.RESET} Request delay: {Colors.YELLOW}{args.delay}{Colors.RESET} seconds")
    if args.timeout != 10:
        print(f"{Colors.CYAN}[*]{Colors.RESET} Request timeout: {Colors.YELLOW}{args.timeout}{Colors.RESET} seconds")
    if args.headers:
        print(f"{Colors.CYAN}[*]{Colors.RESET} Custom headers: {Colors.GREEN}{list(custom_headers.keys())}{Colors.RESET}")
    if args.output:
        print(f"{Colors.CYAN}[*]{Colors.RESET} Output file: {Colors.GREEN}{args.output}{Colors.RESET}")
        # Clear output file if it exists
        open(args.output, 'w').close()
    
    # Process URL(s)
    if args.url:
        target_url = args.url
        if target_url.lower().endswith('.js'):
            analyze_js_file(target_url, headers, args.delay, args.timeout, args.output)
        else:
            scan_url(target_url, headers, args.delay, args.timeout, args.output)
    elif args.list:
        process_url_list(args.list, headers, args.delay, args.timeout, args.output, args.progress)
    
    print(f"\n{Colors.GREEN}[*]{Colors.RESET} Scan complete!")
    if args.output:
        print(f"{Colors.GREEN}[*]{Colors.RESET} Results saved to: {Colors.BLUE}{args.output}{Colors.RESET}")

if __name__ == "__main__":
    main()