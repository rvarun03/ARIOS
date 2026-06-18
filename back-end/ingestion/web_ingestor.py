import requests
from bs4 import BeautifulSoup

from schemas.ingestion import IngestionOutput

def ingest_web(url:str) -> IngestionOutput: 
    
    """
    Web page → Clean structured text
    """

    try:
        response=requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (ARIOS Bot)"
            }
        )
        response.raise_for_status()

        html=response.text

        # 2. Parse HTML
        soup = BeautifulSoup(html, "html.parser")
        
        #3 Remove Junk
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        # 4. Extract title
        title = soup.title.string.strip() if soup.title else None

        #5. Extract text
        text= soup.get_text(separator=" ",  strip= True)

        # 6. Clean extra spaces (basic cleanup)
        clean_text = " ".join(text.split())
         # 7. Return standardized output
        return IngestionOutput(
            source_type="web",
            source_url=url,
            title=title,
            raw_text=clean_text,
            metadata={
                "length": len(clean_text),
                "status_code": response.status_code
            }
        )   

    except:
         return IngestionOutput(
            source_type="web",
            source_url=url,
            title=None,
            raw_text="",
            metadata={
                "error": str(e)
            }
        )    

     
