#!/usr/bin/env python3
"""
Lead scoring system for Justin's Agent - evaluates scraped website content using Google Gemini Pro
"""

import json
import os
import sys
from typing import Dict, Any
import google.generativeai as genai

class LeadScorer:
    def __init__(self, api_key: str = None):
        """Initialize the lead scorer with Google Gemini Pro"""
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            print("Error: Google API key not found!")
            print("Please set the GOOGLE_API_KEY environment variable or pass it as a parameter.")
            print("Get your API key from: https://makersuite.google.com/app/apikey")
            sys.exit(1)
        
        # Configure Google Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def read_website_content(self, filename: str = 'website_context.txt') -> str:
        """Read the scraped website content from file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: {filename} not found!")
            print("Please run crawler.py first to scrape a website.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            sys.exit(1)
    
    def create_evaluation_prompt(self, website_content: str) -> str:
        """Create the evaluation prompt for Gemini"""
        return f"""
You are a lead scoring assistant for Whatnot jewelry sellers. Based on the scraped website content below, return a structured JSON object to help evaluate whether this site is a good fit for Whatnot.

⚠️ Only use information explicitly present in the text. Do not guess or make assumptions. Use evidence from the pages.

Each page is wrapped with [PAGE: URL] to help you reference where the data came from.

---

### Evaluate based on the following criteria (Score each 0-100):

1. **Price Point (< $200)** - MOST IMPORTANT  
   - Score: 0–100  
   - **CRITICAL**: Items under $200 are the strongest indicator for Whatnot
   - List up to 3 items < $200 with their prices (if available)
   - Reference specific page URLs where prices were found
   - **Scoring**: 90-100 if multiple items under $100, 70-89 if items under $200, 50-69 if items under $500

2. **Multi-Channel Selling**  
   - Score: 0–100  
   - Channels checked: Temu, Shein, Alibaba, **Amazon**, **Etsy**, **eBay**, **Instagram**, Facebook, Poshmark, TikTok, **D2C Website**, **Shopify**  
   - Higher signal for bolded channels
   - Reference specific page URLs where channels were found

3. **Contact Info Present**  
   - Score: 0–100  
   - Found: email, phone number, or social media handle  
   - Bonus if linked to a decision-maker
   - List the actual email and phone number found

4. **Vertical Integration**  
   - Score: 0–100  
   - Evidence: mentions of factory, wholesaler, Faire, or Etsy Wholesale
   - Reference specific page URLs where evidence was found

5. **Recent Social Media Activity**  
   - Score: 0–100  
   - Is there any post from 2023–2025 on Instagram or Facebook?
   - Reference specific page URLs where social media was found

---

### Scoring Guidelines:
- **Price Point**: This is the MOST IMPORTANT factor. Sites with items under $200 are excellent Whatnot candidates
- **Channels**: Award points for any social media presence, website, or e-commerce platform
- **Contact**: Give full points for any contact information found
- **Vertical Integration**: Award points for any business-related terms or wholesale mentions
- **Social**: Give points for any social media presence, even if no recent posts mentioned

### IMPORTANT: Do NOT automatically disqualify for:
- Diamonds, engagement rings, custom, handcrafted, or handmade items
- These are just indicators, not automatic disqualifiers
- Focus on the price point as the primary factor

### Only Disqualify If:
- All items are priced over $500  
- Site looks completely outdated or broken  
- No contact information whatsoever  

---

### Total Score (0-100):
The total score should be INDEPENDENT of the individual scores above. It should be your overall assessment based on:
- **Price point is weighted most heavily** (40% of consideration)
- Sites with items under $200 are strong Whatnot candidates
- Consider the overall business model and fit for Whatnot
- This is NOT a sum of the individual scores

---

### Return ONLY a valid JSON object with this format:

```json
{{
  "total_score": 85,
  "disqualified": false,
  "disqualification_reasons": [],
  "scores": {{
    "price": {{
      "score": 95,
      "examples": [
        {{"item": "Silver heart necklace", "price": "$45", "page": "https://example.com/necklaces"}},
        {{"item": "Gold-plated studs", "price": "$35", "page": "https://example.com/earrings"}}
      ]
    }},
    "channels": {{
      "score": 80,
      "found_channels": ["Instagram", "Facebook", "D2C Website"],
      "page_references": ["https://example.com/", "https://example.com/contact"]
    }},
    "contact": {{
      "score": 90,
      "found": ["info@example.com", "+1 (555) 123-4567", "Instagram: @example"],
      "page_references": ["https://example.com/contact"]
    }},
    "vertical_integration": {{
      "score": 75,
      "evidence": "Mentions wholesale and business operations",
      "page_references": ["https://example.com/about"]
    }},
    "social": {{
      "score": 85,
      "evidence": "Active Instagram and Facebook presence found",
      "page_references": ["https://example.com/", "https://example.com/contact"]
    }}
  }},
  "summary": "This site is an excellent fit for Whatnot. It sells affordable jewelry under $200 with strong social media presence, provides clear contact information, and operates as a direct-to-consumer business."
}}
```

---

### Website Content to Analyze:

{website_content}
"""
    
    def evaluate_website(self, website_content: str) -> Dict[str, Any]:
        """Evaluate the website using Gemini Pro"""
        try:
            prompt = self.create_evaluation_prompt(website_content)
            
            print("Analyzing website content with Google Gemini Pro...")
            print("-" * 50)
            
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Try to find JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)
                return result
            else:
                print("Error: Could not extract JSON from Gemini response")
                print("Raw response:", response_text)
                return None
                
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print("Raw response:", response_text)
            return None
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return None
    
    def display_results(self, results: Dict[str, Any]) -> None:
        """Display the evaluation results in a formatted way"""
        if not results:
            print("No results to display.")
            return
        
        print("\n" + "="*60)
        print("LEAD SCORING RESULTS")
        print("="*60)
        
        # Overall score and disqualification
        total_score = results.get('total_score', 0)
        disqualified = results.get('disqualified', False)
        
        print(f"Total Score: {total_score}/100")
        print(f"Status: {'❌ DISQUALIFIED' if disqualified else '✅ QUALIFIED'}")
        
        if disqualified:
            reasons = results.get('disqualification_reasons', [])
            if reasons:
                print("Disqualification Reasons:")
                for reason in reasons:
                    print(f"  • {reason}")
        
        print("\n" + "-"*60)
        print("DETAILED SCORES")
        print("-"*60)
        
        scores = results.get('scores', {})
        
        # Price scoring
        price_data = scores.get('price', {})
        print(f"💰 Price Point (< $200): {price_data.get('score', 0)}/100")
        examples = price_data.get('examples', [])
        if examples:
            print("  Examples:")
            for example in examples:
                print(f"    • {example.get('item', 'N/A')}: {example.get('price', 'N/A')}")
        
        # Channel scoring
        channels_data = scores.get('channels', {})
        print(f"\n🛒 Multi-Channel Selling: {channels_data.get('score', 0)}/100")
        found_channels = channels_data.get('found_channels', [])
        if found_channels:
            print(f"  Found channels: {', '.join(found_channels)}")
        
        # Contact scoring
        contact_data = scores.get('contact', {})
        print(f"\n📞 Contact Info: {contact_data.get('score', 0)}/100")
        found_contact = contact_data.get('found', [])
        if found_contact:
            print(f"  Found: {', '.join(found_contact)}")
        
        # Vertical integration scoring
        vertical_data = scores.get('vertical_integration', {})
        print(f"\n🏭 Vertical Integration: {vertical_data.get('score', 0)}/100")
        evidence = vertical_data.get('evidence', '')
        if evidence:
            print(f"  Evidence: {evidence}")
        
        # Social media scoring
        social_data = scores.get('social', {})
        print(f"\n📱 Recent Social Activity: {social_data.get('score', 0)}/20")
        evidence = social_data.get('evidence', '')
        if evidence:
            print(f"  Evidence: {evidence}")
        
        # Summary
        summary = results.get('summary', '')
        if summary:
            print("\n" + "-"*60)
            print("SUMMARY")
            print("-"*60)
            print(summary)
        
        print("\n" + "="*60)
    
    def save_results(self, results: Dict[str, Any], filename: str = 'scoring_results.json') -> None:
        """Save results to a JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Error saving results: {e}")

def main():
    """Main function to run the lead scoring system"""
    print("Justin's Agent - Lead Scoring System")
    print("="*50)
    
    # Check if website_context.txt exists
    if not os.path.exists('website_context.txt'):
        print("Error: website_context.txt not found!")
        print("Please run crawler.py first to scrape a website.")
        print("Usage: python crawler.py <website_url>")
        sys.exit(1)
    
    # Initialize scorer
    scorer = LeadScorer()
    
    # Read website content
    website_content = scorer.read_website_content()
    
    if not website_content.strip():
        print("Error: website_context.txt is empty!")
        print("Please run crawler.py first to scrape a website.")
        sys.exit(1)
    
    # Evaluate website
    results = scorer.evaluate_website(website_content)
    
    if results:
        # Display results
        scorer.display_results(results)
        
        # Save results
        scorer.save_results(results)
    else:
        print("Failed to evaluate website. Please check your API key and try again.")

if __name__ == "__main__":
    main() 