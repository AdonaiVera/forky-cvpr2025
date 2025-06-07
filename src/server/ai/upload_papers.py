import os
import json
from pathlib import Path
from typing import List, Dict
from pymongo import MongoClient
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
CVPR_PAPERS_URL = "https://storage.googleapis.com/tecla/cvpr2025_papers.json"
CVPR_PAPERS_CACHE_DIR = Path("src/data/cache")
CVPR_PAPERS_CACHE_FILE = CVPR_PAPERS_CACHE_DIR / "cvpr2025_papers.json"

class PaperUploader:
    def __init__(self):
        # Initialize Gemini client
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        genai.configure(api_key=api_key)

        # Initialize MongoDB client
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable is not set")
        self.mongo_client = MongoClient(mongodb_uri)
        self.db = self.mongo_client.cvpr_papers
        self.papers_collection = self.db.papers

    def _create_embedding(self, text: str) -> List[float]:
        """Create embedding for text using Gemini."""
        try:
            response = genai.embed_content(
                model="models/embedding-001",
                content=text
            )
            # Extract embedding from response
            if isinstance(response, dict) and 'embedding' in response:
                return response['embedding']
            return []
        except Exception as e:
            print(f"Error creating embedding: {e}")
            return []

    def _get_papers_data(self) -> Dict:
        """Get CVPR papers data from cache or download."""
        try:
            # Create cache directory if it doesn't exist
            CVPR_PAPERS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

            # Try to read from cache first
            if CVPR_PAPERS_CACHE_FILE.exists():
                with open(CVPR_PAPERS_CACHE_FILE, 'r') as f:
                    return json.load(f)

            # If not in cache, download and save
            import requests
            response = requests.get(CVPR_PAPERS_URL)
            papers_data = response.json()
            
            # Save to cache
            with open(CVPR_PAPERS_CACHE_FILE, 'w') as f:
                json.dump(papers_data, f)
            
            return papers_data

        except Exception as e:
            print(f"Error getting papers data: {e}")
            return {}

    def update_papers(self):
        """Update existing papers in MongoDB Atlas with new data."""
        try:
            # Get papers data
            papers_data = self._get_papers_data()
            if not papers_data:
                print("No papers data available")
                return

            # Process and update papers
            total_papers = len(papers_data)
            updated_count = 0
            for idx, (title, paper) in enumerate(papers_data.items(), 1):
                print(f"Processing paper {idx}/{total_papers}: {title}")

                # Create text for embedding (title + abstract)
                text_for_embedding = f"{title} {paper['abstract']}"
                
                # Generate embedding
                embedding = self._create_embedding(text_for_embedding)
                
                if embedding:
                    # Prepare document for MongoDB
                    paper_doc = {
                        "title": paper["title"],
                        "authors": paper["authors"],
                        "pdf": paper["pdf"],
                        "supp": paper["supp"],
                        "arxiv": paper["arxiv"],
                        "bibtex": paper["bibtex"],
                        "abstract": paper["abstract"],
                        "poster_session": paper["poster_session"],
                        "poster_location": paper["poster_location"],
                        "embedding": embedding
                    }
                    
                    # Update or insert into MongoDB
                    result = self.papers_collection.update_one(
                        {"title": title},
                        {"$set": paper_doc},
                        upsert=True
                    )
                    
                    if result.modified_count > 0 or result.upserted_id:
                        updated_count += 1
                        print(f"Successfully updated paper: {title}")
                else:
                    print(f"Failed to create embedding for paper: {title}")

            print("\nUpdate complete!")
            print(f"Total papers processed: {total_papers}")
            print(f"Papers updated/inserted: {updated_count}")
            print(f"Total papers in database: {self.papers_collection.count_documents({})}")

        except Exception as e:
            print(f"Error updating papers: {e}")

    def upload_papers(self):
        """Process and upload papers to MongoDB Atlas."""
        try:
            # Get papers data
            papers_data = self._get_papers_data()
            if not papers_data:
                print("No papers data available")
                return

            # Clear existing papers
            self.papers_collection.delete_many({})
            print("Cleared existing papers from database")

            # Process and store papers
            total_papers = len(papers_data)
            for idx, (title, paper) in enumerate(papers_data.items(), 1):
                print(f"Processing paper {idx}/{total_papers}: {title}")

                # Create text for embedding (title + abstract)
                text_for_embedding = f"{title} {paper['abstract']}"
                
                # Generate embedding
                embedding = self._create_embedding(text_for_embedding)
                
                if embedding:
                    # Prepare document for MongoDB
                    paper_doc = {
                        "title": paper["title"],
                        "authors": paper["authors"],
                        "pdf": paper["pdf"],
                        "supp": paper["supp"],
                        "arxiv": paper["arxiv"],
                        "bibtex": paper["bibtex"],
                        "abstract": paper["abstract"],
                        "poster_session": paper["poster_session"],
                        "poster_location": paper["poster_location"],
                        "embedding": embedding
                    }
                    
                    # Insert into MongoDB
                    self.papers_collection.insert_one(paper_doc)
                    print(f"Successfully uploaded paper: {title}")
                else:
                    print(f"Failed to create embedding for paper: {title}")

            print("\nUpload complete!")
            print(f"Total papers processed: {total_papers}")
            print(f"Papers in database: {self.papers_collection.count_documents({})}")

        except Exception as e:
            print(f"Error uploading papers: {e}")

def main():
    """Main function to run the upload process."""
    print("Starting CVPR papers upload process...")
    uploader = PaperUploader()
    uploader.update_papers() # or upload_papers()

if __name__ == "__main__":
    main()