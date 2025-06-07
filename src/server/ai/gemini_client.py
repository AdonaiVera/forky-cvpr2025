import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig, GoogleSearch, Tool
from pydantic import BaseModel
from pymongo import MongoClient
import google.generativeai as genaisearch
import requests

# Load environment variables from .env file
load_dotenv()

# Constants for CVPR papers caching
CVPR_PAPERS_CACHE_DIR = Path("src/data/cache")
CVPR_PAPERS_CACHE_FILE = CVPR_PAPERS_CACHE_DIR / "cvpr2025_papers.json"
CVPR_PAPERS_CACHE_MAX_AGE = 24 * 60 * 60  # 24 hours in seconds

class AnalyzeRepositoryResponse(BaseModel):
    summary: str
    use_cases: list[str]
    contribution_insights: list[str]

class SelectIssuesResponse(BaseModel):
    beginner_issues: list[int]
    intermediate_issues: list[int]
    advanced_issues: list[int]

class RepositorySearchResponse(BaseModel):
    repo_full_name: str
    description: str
    language: str
    match_reason: str

class PaperSearchResponse(BaseModel):
    title: str
    authors: list[str]
    pdf: str
    supp: Optional[str]
    arxiv: Optional[str]
    bibtex: Optional[str]
    abstract: str
    poster_session: Optional[str]
    poster_location: Optional[str]

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        self.client = genai.Client(api_key=api_key)
        genaisearch.configure(api_key=api_key)
        self.chat_histories = {}  
        
        # Use MongoDB Atlas vector search to get top 15 similar papers
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable is not set")
        
        self.mongo_client = MongoClient(mongodb_uri)

        self.db = self.mongo_client["cvpr_papers"]

    def _get_cvpr_papers(self) -> dict:
        """
        Get CVPR papers data, using cached version if available and not too old.
        
        Returns
        -------
        dict
            The CVPR papers data
        """
        # Create cache directory if it doesn't exist
        CVPR_PAPERS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

        # Check if cache exists and is not too old
        if CVPR_PAPERS_CACHE_FILE.exists():
            cache_age = time.time() - CVPR_PAPERS_CACHE_FILE.stat().st_mtime
            if cache_age < CVPR_PAPERS_CACHE_MAX_AGE:
                try:
                    with open(CVPR_PAPERS_CACHE_FILE, 'r') as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    print("Error reading cached CVPR papers, will download fresh copy")

        # Download fresh copy if cache doesn't exist or is too old
        try:
            response = requests.get("https://storage.googleapis.com/tecla/cvpr2025_papers.json")
            papers_data = response.json()
            
            # Save to cache
            with open(CVPR_PAPERS_CACHE_FILE, 'w') as f:
                json.dump(papers_data, f)
            
            return papers_data
        except Exception as e:
            print(f"Error downloading CVPR papers: {e}")
            # If download fails and we have a cache, try to use it even if old
            if CVPR_PAPERS_CACHE_FILE.exists():
                try:
                    with open(CVPR_PAPERS_CACHE_FILE, 'r') as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    pass
            return {}
        
    async def search_cvpr_papers(self, query: str) -> list[dict]:
        """
        Search through CVPR 2025 papers based on user query.
        First uses vector search to get top 15 papers, then uses Gemini to rank the top 5.

        Parameters
        ----------
        query : str
            The search query from the user

        Returns
        -------
        list[dict]
            List of top 5 most relevant papers matching the query
        """
        try:
            # Get papers data using cache
            papers_data = self._get_cvpr_papers()
            if not papers_data:
                return []

            # Create embedding for the query
            response = genaisearch.embed_content(
                model="models/embedding-001",
                content=query
            )

            if not response:
                return []

            vector_results = self.db["papers"].aggregate([
                {
                    "$vectorSearch": {
                        "index": "embeddings",
                        "path": "embedding",
                        "queryVector": response['embedding'],
                        "numCandidates": 15,
                        "limit":15
                    }
                }
            ])
            
            
            list_papers = list(vector_results)
            if not list_papers:
                return []

            # Create a simplified version with IDs for Gemini
            simplified_papers = {}
            for idx, paper in enumerate(list_papers):
                simplified_papers[f"paper_{idx}"] = {
                    "id": f"paper_{idx}",
                    "title": paper["title"],
                    "abstract": paper["abstract"]
                }

            # Create the prompt for Gemini to rank top 5
            prompt = f"""
            Given this list of CVPR 2025 papers:
            {json.dumps(simplified_papers, indent=2)}

            And this user query: "{query}"

            Please find the top 5 most relevant papers that match the query. Consider:
            1. Title relevance
            2. Abstract content
            3. Research area/category
            4. Keywords and technical terms

            For each selected paper, provide:
            1. The paper ID
            2. A detailed explanation of why this paper is relevant to the query, including:
               - How the paper's research aligns with the query
               - Key technical contributions that match the query
               - Potential impact or applications related to the query
               - Why someone interested in this query should read this paper

            Return your response as a JSON array with these fields for each paper:
            - "paper_id": The ID of the paper (e.g., "paper_0")
            - "match_reason": A detailed explanation of why this paper matches the query and why it should be read

            Sort the papers by relevance to the query. Return only the top 5 most relevant papers.
            Your response should be ONLY the JSON array, with no additional text or explanation.
            """

            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                },
            )

            if not response or not response.text:
                return []

            # Parse Gemini's response to get ranked papers
            ranked_papers = json.loads(response.text)
            
            # Convert ranked papers to full paper details
            matched_papers = []
            for ranked_paper in ranked_papers:
                paper_id = ranked_paper["paper_id"]
                idx = int(paper_id.split("_")[1])
                paper = list_papers[idx]
                
                # Create PaperSearchResponse and convert to dict
                paper_response = PaperSearchResponse(
                    title=paper["title"],
                    authors=paper["authors"],
                    pdf=paper["pdf"],
                    supp=paper.get("supp"),
                    arxiv=paper.get("arxiv"),
                    bibtex=paper.get("bibtex"),
                    abstract=paper["abstract"],
                    poster_session=paper.get("poster_session"),
                    poster_location=paper.get("poster_location")
                )
                # Add match reason to the response
                paper_dict = paper_response.model_dump()
                paper_dict["match_reason"] = ranked_paper["match_reason"]
                matched_papers.append(paper_dict)
            
            return matched_papers

        except Exception as e:
            print(f"Error searching CVPR papers: {e}")
            return []
