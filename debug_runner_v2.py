
import sys
import io
import scraper
import json
import time

# Force UTF-8 for console output to avoid encoding errors
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_live_search(site):
    print(f"\n{'='*30}")
    print(f"TESTING SITE: {site}")
    print(f"{'='*30}")
    
    try:
        # Use simpler query to increase chance of hits
        # Some sites block complex boolean logic or strict phrases
        query = scraper.generate_search_query(
            role="Atendente", 
            location="Sao Paulo", 
            site=site,
            exact_match=False 
        )
        
        print(f"🔎 Generated Query: {query}")
        
        # Search with debug prints inside scraper
        # We need to monkey-patch or modify scraper to see raw results, 
        # or just use DDGS directly here to see what's coming back.
        from ddgs import DDGS
        print(f"--- Inspecting Raw URLs for {site} ---")
        with DDGS() as ddgs:
             raw = list(ddgs.text(query, max_results=5))
             for r in raw:
                 print(f"RAW URL: {r.get('href', 'No URL')}")
                 print(f"   Title: {r.get('title', 'No Title')}")

        results = scraper.scrape_smart(query, num_results=5, site=site)
        
        if not results:
            print(f"❌ FAILURE: No results found for {site}.")
            print("   Possible causes: IP block, Dork invalid, or no index.")
        else:
            print(f"✅ SUCCESS: Found {len(results)} results.")
            
            print("\n--- Result Sample ---")
            first = results[0]
            print(json.dumps(first, indent=2, ensure_ascii=False))
            
            # Validation
            if "..." in first.get("Nome/Titulo", ""):
                 print("⚠️ WARNING: Title seems truncated.")
            
            if not first.get("Link Perfil"):
                print("❌ BUG: Link is empty!")

    except Exception as e:
        print(f"❌ CRITICAL EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test new X-Ray Modes
    modes = ["Portais de Emprego", "PDF/DOCX - Currículos"]
    for m in modes:
        test_live_search(m)
        time.sleep(2)
