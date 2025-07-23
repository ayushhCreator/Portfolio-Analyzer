"""
News fetching module for Portfolio Analyzer
Integrates news APIs to fetch latest news for holdings
"""

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import yfinance as yf
import re
from datetime import datetime
from typing import List

class NewsFetcher:
    """Handles fetching news for portfolio holdings"""
    
    def get_news_google_rss(self, symbol: str, currency: str) -> List[str]:
        """Get news using Google News RSS (no API key needed, no feedparser required)"""
        try:
            # Get company name for better search
            yf_symbol = f"{symbol}.SI" if currency == 'SGD' else symbol
            try:
                ticker = yf.Ticker(yf_symbol)
                info = ticker.info
                company_name = info.get('longName', '') or info.get('shortName', '') or symbol
            except:
                company_name = symbol

            # Google News RSS URL
            search_query = urllib.parse.quote(f"{symbol} {company_name} stock")
            rss_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-US&gl=US&ceid=US:en"

            # Fetch RSS feed
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            req = urllib.request.Request(rss_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read()

            # Parse XML
            root = ET.fromstring(xml_data)
            
            formatted_news = []
            items = root.findall('.//item')[:5]  # Get first 5 items
            
            if not items:
                return [f"No Google News found for {symbol}"]

            for item in items:
                title_elem = item.find('title')
                link_elem = item.find('link')
                pub_date_elem = item.find('pubDate')
                
                title = title_elem.text if title_elem is not None else 'No title'
                link = link_elem.text if link_elem is not None else '#'
                pub_date = pub_date_elem.text if pub_date_elem is not None else ''
                
                # Clean up title (remove source attribution if present)
                title = re.sub(r' - [^-]*$', '', title)
                
                # Format date
                if pub_date:
                    try:
                        # Parse RFC 2822 date format
                        date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                        date_str = date_obj.strftime('%m/%d')
                        title = f"{title} ({date_str})"
                    except:
                        try:
                            # Alternative date format
                            date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                            date_str = date_obj.strftime('%m/%d')
                            title = f"{title} ({date_str})"
                        except:
                            pass  # Skip date formatting if parsing fails
                
                formatted_news.append(f"• [{title}]({link})")

            return formatted_news if formatted_news else [f"No news found for {symbol}"]

        except urllib.error.URLError as e:
            return [f"Network error fetching Google News: {str(e)}"]
        except ET.ParseError as e:
            return [f"Error parsing Google News RSS: {str(e)}"]
        except Exception as e:
            return [f"An error occurred fetching Google News: {str(e)}"]