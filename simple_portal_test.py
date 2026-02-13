from scraper import generate_search_query, search_candidates, XRAY_MODES
from ddgs import DDGS

def test_portal_query():
    print("Testing Portal Query Generation...")
    role = "Vendedor"
    location = "São José do Rio Preto"
    
    # Generate query for "Portais de Emprego"
    # Mimic the FALLBACK QUERY from scrape_smart
    query = '(site:trabalhabrasil.com.br OR site:infojobs.com.br OR site:vagas.com.br) curriculo "vendedor"' 
    print(f"Generated Query: {query}")
    
    # Try searching
    print("\nAttempting Search...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=20))
            print(f"Found {len(results)} raw results")
            
            with open("debug_output.txt", "w", encoding="utf-8") as f:
                f.write(f"Query: {query}\n\n")
                for i, r in enumerate(results):
                    url = r['href']
                    title = r['title']
                    
                    # Check filtering
                    from scraper import _is_job_posting, _is_valid_result
                    is_valid = _is_valid_result(url, site="Portais de Emprego")
                    is_job_post = _is_job_posting(url, title, site="Portais de Emprego")
                    
                    status = "ACCEPTED" if is_valid and not is_job_post else "REJECTED"
                    reason = []
                    if not is_valid: reason.append("Invalid URL")
                    if is_job_post: reason.append("Job Posting")
                    
                    log_entry = (
                        f"[{i+1}] {title}\n"
                        f"URL: {url}\n"
                        f"Status: {status} ({', '.join(reason)})\n"
                        f"{'-'*40}\n"
                    )
                    f.write(log_entry)
                    
            print("Debug output written to debug_output.txt")
                
    except Exception as e:
        print(f"Search Failed: {e}")
                
    except Exception as e:
        print(f"Search Failed: {e}")

if __name__ == "__main__":
    test_portal_query()
