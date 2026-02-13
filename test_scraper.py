import warnings
warnings.filterwarnings("ignore")
import scraper

def test_query_generation_linkedin():
    query = scraper.generate_search_query("Python Developer", "Sao Paulo", site="LinkedIn")
    print(f"LinkedIn Query: {query}")
    assert 'site:linkedin.com/in' in query
    assert 'Python Developer' in query

def test_query_generation_vagas():
    query = scraper.generate_search_query("Analista", "Rio de Janeiro", site="Vagas.com")
    print(f"Vagas.com Query: {query}")
    assert 'site:vagas.com.br/perfil-de' in query
    assert 'Analista' in query

def test_query_generation_infojobs():
    query = scraper.generate_search_query("Gerente", "Curitiba", site="InfoJobs")
    print(f"InfoJobs Query: {query}")
    assert 'site:infojobs.com.br/candidato' in query
    assert 'Gerente' in query

def test_valid_urls():
    assert scraper._is_valid_result("https://www.linkedin.com/in/joao", site="LinkedIn")
    assert scraper._is_valid_result("https://www.vagas.com.br/perfil-de/maria-123", site="Vagas.com")
    assert scraper._is_valid_result("https://www.infojobs.com.br/candidato/jose-456.aspx", site="InfoJobs")
    assert not scraper._is_valid_result("https://google.com", site="LinkedIn")

def test_clean_title():
    t1 = "Joao Silva - LinkedIn"
    assert scraper._clean_title(t1, "LinkedIn") == "Joao Silva"
    
    t2 = "Curriculum de Maria | Vagas.com.br"
    assert scraper._clean_title(t2, "Vagas.com") == "Maria"

if __name__ == "__main__":
    test_query_generation_linkedin()
    test_query_generation_vagas()
    test_query_generation_infojobs()
    test_valid_urls()
    test_clean_title()
    print("\nAll multi-source tests passed!")
