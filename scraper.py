"""
Candidate Search Scraper - Multi-Source X-Ray Search
Uses ddgs library for reliable search results.
"""
import re
import time
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

from duckduckgo_search import DDGS

# Global Site Configuration (Legacy + New Modes)
# "base": The search operator
# "use_intitle": If we should try intitle:"Role"
# "filetype": Optional filetype restriction
# "site_filter": Optional list of sites to search within (OR logic)

XRAY_MODES = {
    "LinkedIn": {
        'base': 'site:linkedin.com/in', 
        'use_intitle': True,
        'name': 'Perfil LinkedIn'
    },
    "PDF/DOCX - Currículos": {
        'base': '("curriculum" OR "cv") (filetype:pdf OR filetype:docx OR filetype:doc) -relatório -edital -manual -ementa -diário', 
        'use_intitle': False, 
        'name': 'Arquivos (PDF/DOC)'
    },
    "Portais de Emprego": {
        'base': '(site:trabalhabrasil.com.br OR site:bne.com.br OR site:catho.com.br OR site:infojobs.com.br OR site:vagas.com.br) (inurl:curriculo OR inurl:perfil OR inurl:candidato)', 
        'use_intitle': False, 
        'name': 'Portais (TrabalhaBrasil, BNE, etc)'
    },
    "Redes Sociais": {
        'base': 'site:instagram.com OR site:facebook.com', 
        'use_intitle': False, 
        'name': 'Redes Sociais (Instagram/Facebook)'
    },
    "Listas de RH": {
        'base': '(filetype:xls OR filetype:xlsx OR filetype:csv) ("lista de candidatos" OR "banco de talentos")', 
        'use_intitle': False, 
        'name': 'Planilhas de RH'
    }
}

# Legacy mapping for compatibility if needed (can be removed later)
SITE_CONFIG = XRAY_MODES 


def generate_search_query(role, location, seniority="", skills="", exact_match=False,
                          exclude_terms="", target_company="", use_intitle=False,
                          open_to_work=False, site="LinkedIn"):
    """
    Generates a search query for different platforms/modes.
    """
    
    # Get config for the selected mode, default to LinkedIn if not found
    config = XRAY_MODES.get(site, XRAY_MODES["LinkedIn"])
    base_dork = config['base']
    
    # 1. Start with the Site/Filetype operator
    query_parts = [base_dork]

    # 2. Add Role and Location
    # For filetypes, we ALWAYS want the role to be prominent
    # And we add "bio" keywords to ensure it's a person
    if "filetype" in base_dork and "Lista" not in site:
         query_parts.append(f'"{role}"')
         query_parts.append(f'"{location}"')
         # FORCE resume keywords to avoid "price lists" or "reports"
         query_parts.append('("experiência" OR "formação" OR "educação" OR "contato")')
    else:
        # Standard site search
        if exact_match or config['use_intitle']:
             if config.get('use_intitle'):
                 query_parts.append(f'intitle:"{role}"')
             else:
                 query_parts.append(f'"{role}"')
             query_parts.append(f'"{location}"')
        else:
             query_parts.append(role)
             query_parts.append(f'"{location}"') # Keep location quoted for accuracy

    # 3. Add Seniority
    if seniority:
        query_parts.append(f'"{seniority}"')

    # 4. Add Skills
    if skills:
        if "," in skills:
            skills_list = [s.strip() for s in skills.split(",") if s.strip()]
            query_parts.append('(' + " OR ".join([f'"{s}"' for s in skills_list]) + ')')
        else:
            query_parts.append(f'"{skills.strip()}"')

    # 5. Target Company
    if target_company:
        companies = [c.strip() for c in target_company.split(",") if c.strip()]
        if len(companies) > 1:
            query_parts.append('(' + " OR ".join([f'"{c}"' for c in companies]) + ')')
        elif companies:
            query_parts.append(f'"{companies[0]}"')

    # 6. Exclude Terms
    if exclude_terms:
        for term in exclude_terms.split(","):
            term = term.strip()
            if term:
                query_parts.append(f'-{term}')

    # 7. Open to Work / Availability
    if open_to_work:
        # Keywords that suggest immediate availability
        query_parts.append('("open to work" OR "aberto a propostas" OR "disponível" OR "imediato" OR "cv")')

    return " ".join(query_parts).strip()


def _is_valid_result(url, site="LinkedIn"):
    """Checks if the URL matches the expected pattern for the selected mode."""
    if not url: return False
    url = url.lower()

    # 1. LinkedIn Mode
    if site == "LinkedIn":
        return "linkedin.com/in/" in url

    # 2. Files Mode (PDF/DOCX)
    if "PDF" in site or "Lista" in site:
        valid_extensions = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.xls', '.xlsx', '.csv']
        return any(url.endswith(ext) for ext in valid_extensions)

    # 3. Portals Mode
    if "Portais" in site:
        # Strict Paths for Portals
        # If url doesn't match one of these specific "candidate" patterns, kill it
        portal_patterns = [
            (r'trabalhabrasil\.com\.br/curriculo', 'TrabalhaBrasil'),
            (r'bne\.com\.br/(curriculo|vagas-de-emprego)', 'BNE'), # BNE sometimes puts resumes under odd paths, but let's stick to curriculo if possible
            (r'catho\.com\.br/(perfil|curriculo|profissional)', 'Catho'),
            (r'infojobs\.com\.br/(candidato|cv|curriculo)', 'InfoJobs'),
            (r'vagas\.com\.br/(perfil-de|curriculo/|profissionais)', 'Vagas.com'),
        ]
        
        # Special BNE case: BNE often has 'vagas-de-emprego' in the title even for candidates? No, usually candidates are 'vip'.
        # Let's be strict: if it's BNE, must be /curriculo/ or /vip/
        if "bne.com.br" in url:
             return "/curriculo/" in url or "/vip/" in url
             
        # General check for others
        for pat, name in portal_patterns:
            if name.lower().replace(".com", "").replace(".br", "") in url:
                if re.search(pat, url, re.IGNORECASE):
                    # Extra check for Vagas: 'curriculo' must be folder, not part of slug if possible
                    if "vagas.com.br" in url and "curriculo" in url and "/curriculo/" not in url:
                         # Reject 'curriculo-de-vendedor' (article) but accept 'curriculo/id'
                         return False 
                    return True
                return False # Domain matched but path didn't -> Job posting or home page
                
        # If domain not in our specific list but was passed (e.g. indeed/glassdoor if we added them), default to False to be safe
        return False

    # 4. Social Mode
    if "Redes" in site:
        return "instagram.com" in url or "facebook.com" in url

    # Default fallback (should catch most things if logic is sound)
    return True


def _clean_title(title, site="LinkedIn"):
    """Cleans the page title."""
    if not title:
        return ""
        
    title = title.strip()
    
    if site == "LinkedIn":
        for suffix in [" - LinkedIn", " | LinkedIn", " - Brasil", " - Brazil"]:
            title = title.replace(suffix, "")
    elif site == "Vagas.com":
        title = title.replace(" | Vagas.com.br", "").replace("Curriculum de ", "").replace(" - Vagas.com.br", "")
    elif site == "InfoJobs":
        title = title.replace(" | InfoJobs", "").replace("CV de ", "").replace(" - InfoJobs", "")
    elif site == "Catho":
        title = title.replace(" | Catho", "").replace(" - Catho", "")
        
    return title.strip()


def _extract_email(text):
    if not text:
        return "N/A"
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else "N/A"


def _is_job_posting(url, title, site="LinkedIn"):
    """
    Returns True if the result is likely a job posting, False if it's a candidate.
    """
    
    # 1. URL Path Checks (Jobs usually have specific paths)
    job_paths = [
        "/vaga/", "/vagas/", "/job/", "/jobs/", "/oportunidade/", "/oportunidades/",
        "/empresa/", "/empresas/", "/company/", "/companies/",
        "/login", "/signin", "/cadastro", "/home", "/search", "/busca",
        "/trabalhe-conosco", "/carreiras", "/blog/", "/artigo/", "/noticia/"
    ]
    
    # Exclude specific non-candidate subdomains/paths
    if "profissoes.vagas.com.br" in url: return True
    if "blog." in url: return True
    
    if any(p in url.lower() for p in job_paths):
        return True

    # 2. Title Checks (Jobs usually start with "Vaga de..." or similar)
    title_lower = title.lower()
    
    # Generic non-candidate titles
    bad_starts = (
        "vaga de", "vagas de", "oportunidade de", "estágio em", "trabalhe conosco",
        "como criar", "modelo de", "dicas para", "o que faz", "quanto ganha"
    )
    if title_lower.startswith(bad_starts):
        return True
        
    if "vagas.com.br" in url and ("| vagas.com" in title_lower or "- vagas.com" in title_lower):
        if "vaga de" in title_lower or "oportunidade" in title_lower:
            return True

    return False



def search_candidates(query, num_results=10, site="LinkedIn", expected_location=None):
    """
    Search using DDG API with retry/error handling.
    """
    results = []

    print(f"[Search][{site}] Query: {query[:80]}...")
    
    raw = []
    try:
        # DDGS can be flaky, so we wrap it
        with DDGS() as ddgs:
            # Fetch a bit more to allow for valid url filtering
            gen = ddgs.text(query, max_results=min(num_results * 5, 60))
            raw = list(gen)
            
    except Exception as e:
        print(f"[Results] Error during DDGS search: {e}")
        return []

    print(f"[Search] Got {len(raw)} raw results")

    for item in raw:
        url = item.get("href", "")
        title = item.get("title", "")
        body = item.get("body", "")
        
        # Determine if it is a VALID candidate profile
        is_candidate = False
        
        # 1. Check if valid basic URL pattern matches
        if _is_valid_result(url, site):
             is_candidate = True
        
        # 2. Double check: Ensure it's NOT a job posting
        if _is_job_posting(url, title, site):
            is_candidate = False
            
        # 3. Document Title Check
        if "PDF" in site or "Lista" in site:
            # Filter out non-resume titles
            bad_titles = ["relatório", "report", "ata de", "diário oficial", "edital", "manual", "preço", "cotação", "boleto", "invoice", "nota fiscal"]
            if any(bt in title.lower() for bt in bad_titles):
                is_candidate = False

        # 4. Strict Location Check
        if is_candidate and expected_location:
            loc_lower = expected_location.lower().strip()
            # Check if location is in title or body
            # We must be careful not to filter out good results if snippet is short
            # But the user specifically complained about wrong locations, so strict is better.
            combined_text = (title + " " + body).lower()
            
            # Simple check
            if loc_lower not in combined_text:
                 # Try to be smart about "sao jose do rio preto" -> "s.j. do rio preto"
                 # normalization mapping could go here, but for now exact match is safest request
                 # Maybe allow partial match if location is long?
                 # No, user wants SPECIFIC city.
                 is_candidate = False
            
        if is_candidate:
            results.append({
                "Nome/Titulo": _clean_title(title, site),
                "Link Perfil": url,
                "Resumo": body,
                "Email": _extract_email(body),
                "Fonte": site
            })

        if len(results) >= num_results:
            break

    print(f"[Search] Found {len(results)} {site} profiles")
    return results


def deduplicate_results(results):
    seen_urls = set()
    unique = []

    for item in results:
        link = item.get("Link Perfil", "").lower()
        if link not in seen_urls:
            seen_urls.add(link)
            unique.append(item)

    return unique


def scrape_smart(query, num_results=10, site="LinkedIn", expected_location=None, **kwargs):
    """
    Main search function with fallback strategies.
    """
    print("=" * 50)

    data = search_candidates(query, num_results=num_results, site=site, expected_location=expected_location)

    # Fallback Logic
    if not data:
        print(f"[Fallback] No results for {site}. Trying simplified query...")
        time.sleep(1.5) # Wait a bit to be polite
        
        # 1. Remove specific dork patterns
        simplified = query
        if "site:" in simplified:
             # Remove the specific site dork from config
             for k, v in XRAY_MODES.items():
                 # Handle cases where base has OR logic
                 bases = v['base'].replace("(", "").replace(")", "").split(" OR ")
                 for b in bases:
                     if b.strip() in simplified:
                         simplified = simplified.replace(b.strip(), "").strip()
        
        # 2. Append a simpler site restriction
        if site == "LinkedIn":
            simplified = f"{simplified} LinkedIn perfil"
        elif site == "Portais de Emprego":
            simplified = f"{simplified} (site:trabalhabrasil.com.br OR site:infojobs.com.br OR site:vagas.com.br) curriculo"
        elif site == "PDF/DOCX - Currículos":
             simplified = f"{simplified} (filetype:pdf OR filetype:docx) curriculo"
        elif site == "Redes Sociais":
             simplified = f"{simplified} (site:instagram.com OR site:facebook.com)"
        elif site == "Listas de RH":
             simplified = f"{simplified} (filetype:xls OR filetype:csv) lista candidatos"
             
        # 3. Remove complex operators that might confuse the engine, but keep quotes for multi-word terms
        simplified = simplified.replace("intitle:", "")
        
        # Only remove quotes if they are single words inside (e.g. "Python"), but complex locations need quotes.
        # For now, let's just keep the quotes as DDG handles them better than loose words for cities.
        # specific fix: ensure we don't have empty quotes
        simplified = simplified.replace('""', "")
        
        print(f"[Fallback] Query: {simplified}")
        
        if simplified != query:     
            data = search_candidates(simplified, num_results=num_results, site=site, expected_location=expected_location)

    data = deduplicate_results(data)

    print("=" * 50)
    print(f">> Total: {len(data)} unique {site} profiles")

    return data
