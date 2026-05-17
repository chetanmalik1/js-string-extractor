import os
import requests
from urllib.parse import urlparse

def sanitize_filename(url):
    """Create a safe filename from the URL."""
    parsed = urlparse(url)
    safe_name = f"{parsed.netloc}{parsed.path}"
    # Replace characters that are not alphanumeric, dot, underscore, or hyphen with underscore
    safe_name = "".join([c if c.isalnum() or c in ['.', '_', '-'] else '_' for c in safe_name])
    
    # If the filename becomes empty, give it a default name
    if not safe_name.strip('_'):
        safe_name = "page_content"
    return safe_name

def crawl_and_save(input_file, output_dir):
    """Reads URLs from input_file, fetches them, and saves to output_dir."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print(f"No URLs found in {input_file}.")
        return

    for i, url in enumerate(urls):
        print(f"Fetching [{i+1}/{len(urls)}]: {url}")
        
        # Add scheme if missing
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url

        try:
            # Masking as a standard browser to avoid basic bot blocks
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            # Generate a safe, unique filename
            filename = sanitize_filename(url)
            filename = f"{i+1}_{filename}.txt"  # Prepend index to guarantee uniqueness
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as out_f:
                # Top of the file includes the original URL link
                out_f.write(f"=========================================\n")
                out_f.write(f"Source URL: {url}\n")
                out_f.write(f"=========================================\n\n")
                out_f.write(response.text)
            
            print(f" -> Saved successfully to: {filepath}\n")

        except Exception as e:
            print(f" -> Failed to fetch {url}: {e}\n")

if __name__ == "__main__":
    input_urls_file = "urls.txt"
    output_directory = "downloaded_pages"
    
    # Generate a dummy input file if it does not exist
    if not os.path.exists(input_urls_file):
        print(f"[!] Input file '{input_urls_file}' not found.")
        print(f"[*] Creating a sample '{input_urls_file}' for you...")
        with open(input_urls_file, 'w') as f:
            f.write("https://example.com\n")
            f.write("https://code.jquery.com/jquery-3.6.0.min.js\n")
        print(f"[*] Please add your target URLs (one per line) to '{input_urls_file}' and run the script again.")
    else:
        crawl_and_save(input_urls_file, output_directory)
