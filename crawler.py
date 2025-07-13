#!/usr/bin/env python3
"""
Web crawler for Justin's Agent - scrapes internal pages and extracts clean text
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
from typing import Set, List
import sys

class WebsiteCrawler:
    def __init__(self, base_url: str, max_pages: int = 20):
        self.base_url = base_url
        self.max_pages = max_pages
        self.visited_urls: Set[str] = set()
        self.pages_to_visit: List[str] = [base_url]
        self.domain = urlparse(base_url).netloc
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def is_internal_link(self, url: str) -> bool:
        """Check if URL is internal to the same domain"""
        parsed = urlparse(url)
        return parsed.netloc == self.domain or not parsed.netloc
    
    def clean_text(self, html_content: str) -> str:
        """Extract clean text from HTML using BeautifulSoup"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_links(self, html_content: str, current_url: str) -> List[str]:
        """Extract internal links from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(current_url, href)
            
            # Only include internal links that we haven't visited
            if (self.is_internal_link(full_url) and 
                full_url not in self.visited_urls and
                full_url not in self.pages_to_visit):
                links.append(full_url)
        
        return links
    
    def crawl(self, progress_callback=None) -> None:
        """Main crawling function"""
        if progress_callback:
            progress_callback(f"Starting crawl of {self.base_url}")
            progress_callback(f"Domain: {self.domain}")
            progress_callback(f"Max pages: {self.max_pages}")
            progress_callback("-" * 50)
        else:
            print(f"Starting crawl of {self.base_url}")
            print(f"Domain: {self.domain}")
            print(f"Max pages: {self.max_pages}")
            print("-" * 50)
        
        pages_crawled = 0
        
        with open('website_context.txt', 'w', encoding='utf-8') as f:
            while self.pages_to_visit and pages_crawled < self.max_pages:
                current_url = self.pages_to_visit.pop(0)
                
                if current_url in self.visited_urls:
                    continue
                
                try:
                    status_msg = f"Crawling {pages_crawled + 1}/{self.max_pages}: {current_url}"
                    if progress_callback:
                        progress_callback(status_msg)
                    else:
                        print(status_msg)
                    
                    response = requests.get(current_url, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    
                    # Clean the text
                    clean_text = self.clean_text(response.text)
                    
                    # Write to file with page segmentation
                    f.write(f"[PAGE: {current_url}]\n")
                    f.write(clean_text)
                    f.write("\n\n")
                    f.flush()  # Ensure content is written immediately
                    
                    # Extract new links
                    new_links = self.extract_links(response.text, current_url)
                    self.pages_to_visit.extend(new_links)
                    
                    # Mark as visited
                    self.visited_urls.add(current_url)
                    pages_crawled += 1
                    
                    # Be respectful with delays
                    time.sleep(1)
                    
                except Exception as e:
                    error_msg = f"Error crawling {current_url}: {e}"
                    if progress_callback:
                        progress_callback(error_msg)
                    else:
                        print(error_msg)
                    self.visited_urls.add(current_url)
                    continue
        
        completion_msg = f"\nCrawl completed! Crawled {pages_crawled} pages."
        save_msg = f"Results saved to website_context.txt"
        
        if progress_callback:
            progress_callback(completion_msg)
            progress_callback(save_msg)
        else:
            print(completion_msg)
            print(save_msg)

def main():
    if len(sys.argv) != 2:
        print("Usage: python crawler.py <website_url>")
        print("Example: python crawler.py https://example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        crawler = WebsiteCrawler(url)
        crawler.crawl()
    except KeyboardInterrupt:
        print("\nCrawl interrupted by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 