import sys
import argparse
import requests
from urllib.parse import urlparse

def extract_filename(url):
    path = urlparse(url).path
    filename = path.split('/')[-1]
    return filename if filename else 'index.html'

def main():
    parser = argparse.ArgumentParser(description="Fetch URLs and save contents to a single text file.")
    parser.add_argument('input_file', help="File containing list of URLs")
    parser.add_argument('output_file', help="Single output file to store all downloaded contents")
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    total = len(urls)
    if total == 0:
        print("No URLs found in the input file.")
        return

    print(f"Starting fetch for {total} URLs...\n")

    # Headers to mimic a real browser
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    with open(args.output_file, 'w', encoding='utf-8') as out_f:
        for idx, url in enumerate(urls, 1):
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'http://' + url
                
            filename = extract_filename(url)
            
            # Real-time progress update replacing the current line
            progress_msg = f"[{idx}/{total}] Fetching: {url} | Saving file: {filename}"
            # Ensure it fits nicely and clears previous long strings
            sys.stdout.write(f"\r\033[K{progress_msg[:120]}") 
            sys.stdout.flush()

            try:
                response = requests.get(url, headers=headers, timeout=10)
                content = response.text

                # Write to the single output file
                out_f.write(f"{'/'*80}\n")
                out_f.write(f"// URL: {url}\n")
                out_f.write(f"// File Name: {filename}\n")
                out_f.write(f"{'/'*80}\n\n")
                out_f.write(content)
                out_f.write("\n\n")
                
            except Exception as e:
                # Still output an error block if it failed
                out_f.write(f"{'!'*80}\n")
                out_f.write(f"// URL: {url}\n")
                out_f.write(f"// FAILED TO FETCH: {e}\n")
                out_f.write(f"{'!'*80}\n\n")
    
    # Clear the progress line and finish
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()
    print(f"Done! All contents saved to {args.output_file}")

if __name__ == "__main__":
    main()
