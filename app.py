#!/usr/bin/env python3
"""
Justin's Agent - Lead Qualification Pipeline
Streamlit web interface for web scraping and lead scoring
"""

import streamlit as st
import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path to import our modules
sys.path.append(str(Path(__file__).parent))

# Import our existing modules
from crawler import WebsiteCrawler
from scorer import LeadScorer

def main():
    st.set_page_config(
        page_title="Justin's Agent - Lead Qualification",
        page_icon="🍊",
        layout="wide"
    )
    
    st.title("🍊 Justin's Agent - Lead Qualification Pipeline")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Use the built-in API key from Streamlit secrets
        api_key = st.secrets.get('GOOGLE_API_KEY')
        
        if not api_key:
            st.warning("⚠️ API key not found in secrets. Using placeholder for testing.")
            api_key = "test_key_for_demo"
        
        st.success("✅ Orange Slice Agent ready!")
        
        # Max pages configuration
        max_pages = st.slider(
            "Max Pages to Crawl",
            min_value=5,
            max_value=50,
            value=20,
            help="Maximum number of pages to crawl from the website"
        )
        
        st.markdown("---")
        st.markdown("### How it works:")
        st.markdown("1. **Crawl**: Scrapes website pages and extracts clean text")
        st.markdown("2. **Score**: Uses Justin's Orange Slice Agent to evaluate lead qualification")
        st.markdown("3. **Results**: Shows detailed scoring and recommendations")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🔍 Website Analysis")
        
        # URL input
        url = st.text_input(
            "Enter Website URL",
            placeholder="https://example.com",
            help="Enter the website URL you want to analyze"
        )
        
        # Validate URL
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Analysis button
        analyze_button = st.button(
            "🚀 Analyze Website",
            type="primary",
            disabled=not url,
            help="Start the crawling and scoring process"
        )
    
    with col2:
        st.header("📊 Scoring Criteria")
        st.markdown("**Price Point** (< $200)")
        st.markdown("**Multi-Channel** (Amazon, Etsy, etc.)")
        st.markdown("**Contact Info** (email, phone)")
        st.markdown("**Vertical Integration** (factory, wholesale)")
        st.markdown("**Social Activity** (2023-2025)")
        
        st.markdown("---")
        st.markdown("**Total Score: 0-100**")
        st.markdown("**Auto-disqualify** if criteria not met")
    
    # Main analysis logic
    if analyze_button and url:
        try:
            # API key is already available from st.secrets
            
            # Step 1: Crawl the website
            st.subheader("🕷️ Website Crawling Progress")
            
            # Create containers for different types of messages
            status_container = st.container()
            current_page_container = st.container()
            completion_container = st.container()
            
            # Track if we've shown the initial status
            status_shown = False
            
            def progress_callback(message):
                nonlocal status_shown
                
                if message.startswith("Starting crawl"):
                    with status_container:
                        st.info(message)
                elif message.startswith("Domain:"):
                    with status_container:
                        st.text(message)
                elif message.startswith("Max pages:"):
                    with status_container:
                        st.text(message)
                elif message.startswith("-" * 50):
                    with status_container:
                        st.text(message)
                elif message.startswith("Crawling"):
                    # Clear previous current page and show new one
                    current_page_container.empty()
                    with current_page_container:
                        st.info(message)
                elif message.startswith("Error"):
                    with current_page_container:
                        st.error(message)
                elif message.startswith("Crawl completed"):
                    with completion_container:
                        st.success(message)
                elif message.startswith("Results saved"):
                    with completion_container:
                        st.success(message)
            
            with st.spinner("🕷️ Crawling website pages..."):
                crawler = WebsiteCrawler(url, max_pages=max_pages)
                crawler.crawl(progress_callback=progress_callback)
                
                st.success(f"✅ Crawled {len(crawler.visited_urls)} pages successfully!")
            
            # Step 2: Score the lead
            with st.spinner("🍊 Analyzing with Justin's Orange Slice Agent..."):
                st.info("Evaluating website content for lead qualification")
                
                scorer = LeadScorer(api_key)
                website_content = scorer.read_website_content()
                
                if not website_content.strip():
                    st.error("❌ No content found to analyze. Please try a different website.")
                    return
                
                # Check if we're in test mode
                if api_key == "test_key_for_demo":
                    st.warning("🧪 **TEST MODE**: Showing sample results (no API call made)")
                    
                    # Create sample results for testing
                    results = {
                        "total_score": 85,
                        "disqualified": False,
                        "disqualification_reasons": [],
                        "scores": {
                            "price": {
                                "score": 18,
                                "examples": [
                                    {"item": "Sterling Silver Necklace", "price": "$45", "page": "https://example.com/necklaces"},
                                    {"item": "Gold-plated Studs", "price": "$35", "page": "https://example.com/earrings"}
                                ]
                            },
                            "channels": {
                                "score": 18,
                                "found_channels": ["Instagram", "Facebook", "D2C Website"],
                                "page_references": ["https://example.com/", "https://example.com/contact"]
                            },
                            "contact": {
                                "score": 20,
                                "found": ["info@example.com", "+1 (555) 123-4567", "Instagram: @example"],
                                "page_references": ["https://example.com/contact"]
                            },
                            "vertical_integration": {
                                "score": 15,
                                "evidence": "Mentions wholesale and business operations",
                                "page_references": ["https://example.com/about"]
                            },
                            "social": {
                                "score": 14,
                                "evidence": "Active Instagram and Facebook presence found",
                                "page_references": ["https://example.com/", "https://example.com/contact"]
                            }
                        },
                        "summary": "This site is an excellent fit. It sells affordable jewelry with strong social media presence, provides clear contact information, and operates as a direct-to-consumer business."
                    }
                else:
                    results = scorer.evaluate_website(website_content)
                    
                    if not results:
                        st.error("❌ Failed to analyze website. Please check your Orange Slice Agent API key and try again.")
                        return
                
                st.success("✅ Analysis complete!")
            
            # Step 3: Display results
            st.markdown("---")
            st.header("📈 Analysis Results")
            
            # Overall score and status
            total_score = results.get('total_score', 0)
            disqualified = results.get('disqualified', False)
            
            # Create score display
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Score",
                    f"{total_score}/100",
                    delta=None
                )
            
            with col2:
                status = "❌ DISQUALIFIED" if disqualified else "✅ QUALIFIED"
                st.metric("Status", status)
            
            with col3:
                if disqualified:
                    st.error("Lead Disqualified")
                else:
                    if total_score >= 80:
                        st.success("High Priority Lead")
                    elif total_score >= 60:
                        st.warning("Medium Priority Lead")
                    else:
                        st.info("Low Priority Lead")
            
            # Disqualification warning
            if disqualified:
                reasons = results.get('disqualification_reasons', [])
                if reasons:
                    st.error("🚫 **Disqualification Reasons:**")
                    for reason in reasons:
                        st.error(f"• {reason}")
            
            # Detailed scores
            st.subheader("📊 Detailed Scoring")
            
            scores = results.get('scores', {})
            
            # Create columns for score display
            score_cols = st.columns(2)
            
            # Price scoring
            with score_cols[0]:
                price_data = scores.get('price', {})
                price_score = price_data.get('score', 0)
                
                st.metric("💰 Price Point (< $200)", f"{price_score}/20")
                
                examples = price_data.get('examples', [])
                if examples:
                    st.markdown("**Examples:**")
                    for example in examples:
                        page_ref = example.get('page', '')
                        page_text = f" (from {page_ref})" if page_ref else ""
                        st.markdown(f"• {example.get('item', 'N/A')}: {example.get('price', 'N/A')}{page_text}")
            
            # Channel scoring
            with score_cols[1]:
                channels_data = scores.get('channels', {})
                channels_score = channels_data.get('score', 0)
                
                st.metric("🛒 Multi-Channel Selling", f"{channels_score}/20")
                
                found_channels = channels_data.get('found_channels', [])
                page_refs = channels_data.get('page_references', [])
                if found_channels:
                    st.markdown("**Found channels:**")
                    st.markdown(f"• {', '.join(found_channels)}")
                    if page_refs:
                        st.markdown("**Found on pages:**")
                        for page in page_refs:
                            st.markdown(f"  - {page}")
            
            # Contact scoring
            with score_cols[0]:
                contact_data = scores.get('contact', {})
                contact_score = contact_data.get('score', 0)
                
                st.metric("📞 Contact Info", f"{contact_score}/20")
                
                found_contact = contact_data.get('found', [])
                page_refs = contact_data.get('page_references', [])
                if found_contact:
                    st.markdown("**Found:**")
                    for contact in found_contact:
                        st.markdown(f"• {contact}")
                    if page_refs:
                        st.markdown("**Found on pages:**")
                        for page in page_refs:
                            st.markdown(f"  - {page}")
            
            # Vertical integration scoring
            with score_cols[1]:
                vertical_data = scores.get('vertical_integration', {})
                vertical_score = vertical_data.get('score', 0)
                
                st.metric("🏭 Vertical Integration", f"{vertical_score}/20")
                
                evidence = vertical_data.get('evidence', '')
                page_refs = vertical_data.get('page_references', [])
                if evidence:
                    st.markdown("**Evidence:**")
                    st.markdown(f"• {evidence}")
                    if page_refs:
                        st.markdown("**Found on pages:**")
                        for page in page_refs:
                            st.markdown(f"  - {page}")
            
            # Social media scoring
            with score_cols[0]:
                social_data = scores.get('social', {})
                social_score = social_data.get('score', 0)
                
                st.metric("📱 Recent Social Activity", f"{social_score}/20")
                
                evidence = social_data.get('evidence', '')
                page_refs = social_data.get('page_references', [])
                if evidence:
                    st.markdown("**Evidence:**")
                    st.markdown(f"• {evidence}")
                    if page_refs:
                        st.markdown("**Found on pages:**")
                        for page in page_refs:
                            st.markdown(f"  - {page}")
            
            # Summary
            summary = results.get('summary', '')
            if summary:
                st.subheader("📝 Summary")
                st.info(summary)
            
            # Raw JSON (collapsible)
            with st.expander("🔧 Raw JSON Data"):
                st.json(results)
            
            # Download results
            st.subheader("💾 Download Results")
            
            # JSON download
            json_str = json.dumps(results, indent=2, ensure_ascii=False)
            st.download_button(
                label="📄 Download JSON Results",
                data=json_str,
                file_name=f"lead_analysis_{url.replace('://', '_').replace('/', '_')}.json",
                mime="application/json"
            )
            
            # Website context download
            if os.path.exists('website_context.txt'):
                with open('website_context.txt', 'r', encoding='utf-8') as f:
                    context_data = f.read()
                
                st.download_button(
                    label="📄 Download Scraped Content",
                    data=context_data,
                    file_name=f"website_context_{url.replace('://', '_').replace('/', '_')}.txt",
                    mime="text/plain"
                )
        
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.error("Please check your URL and API key, then try again.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "🍊 Justin's Agent - Lead Qualification Pipeline | "
        "Built with Love <3"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 