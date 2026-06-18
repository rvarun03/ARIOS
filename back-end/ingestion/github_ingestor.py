from git import Repo
import tempfile
import shutil
import os
from schemas.ingestion import IngestionOutput

### Cloning the repo

def clone_repo(repo_url: str):

    temp_dir = tempfile.mkdtemp()

    Repo.clone_from(
        repo_url,
        temp_dir
    )

    return temp_dir


### Reading the files

def extract_repo_text(repo_path:str) -> str:

    texts=[]

    allow_extensions={
        ".py",
        ".md",
        ".txt"
    }

    for root,_,files in os.walk(repo_path):

        for file in files:
            ## split the filename into name and extension like app and .py, then compare it with 

            ext= os.path.splitext(file)[1]

            if ext not in allow_extensions:
                continue

            filepath= os.path.join(root,file)

            try:

                with open(
                    filepath,
                    "r",
                    encoding="utf-8"
                ) as f:

                    texts.append(f.read())
                
            except:
                continue

    return "\n".join(texts)

def ingest_github(repo_url:str):

    temp_dir=None

    try:

        temp_dir= clone_repo(repo_url)

        raw_text= extract_repo_text(temp_dir)

        return IngestionOutput(
            source_type="github",
            source_url=repo_url,
            title=None,
            raw_text=raw_text,
            metadata={
                "length": len(raw_text)
            }
        )
    
    except Exception as e:

        return IngestionOutput(
            source_type="github",
            source_url=repo_url,
            title=None,
            raw_text="",
            metadata={
                "error": str(e)
            }
        )
    
    finally:

        if temp_dir:
            shutil.rmtree(temp_dir)
