
import scraper
import json

def test_live_search(site):
    print(f"\n--- Testing Live Search: {site} ---")
    
    # Generic query that should return results
    query = scraper.generate_search_query(
        role="Atendente", 
        location="Sao Paulo", 
        site=site
    )
    
    print(f"Query: {query}")
    
    try:
        # Search for just 3 results to verify connectivity and parsing
        results = scraper.scrape_smart(query, num_results=3, site=site)
        
        if not results:
            print(f"❌ WARNING: No results found for {site}.")
        else:
            print(f"✅ Success: Found {len(results)} results.")
            print("First result sample:")
            print(json.dumps(results[0], indent=2, ensure_ascii=False))
            
            # Validation check
            first = results[0]
            if not first.get("Link Perfil"):
                print("❌ BUG: Missing Link Perfil")
            if not first.get("Nome/Titulo"):
                print("❌ BUG: Missing Title")
                
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_live_search("Vagas.com")
    test_live_search("InfoJobs")
    test_live_search("Catho")
