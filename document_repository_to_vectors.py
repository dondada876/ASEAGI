#!/usr/bin/env python3
"""
Document Repository to Vector Databases (Option 2)
Uploads extracted documents to Qdrant, Pinecone, or both with embeddings
Supports semantic search using vector similarity
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import hashlib

# Embedding generation
try:
    import openai
except ImportError:
    print("[WARN] Installing openai library...")
    os.system("pip install openai")
    import openai

# Qdrant client
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    QdrantClient = None
    print("[WARN] Qdrant not installed. Install with: pip install qdrant-client")

# Pinecone client
try:
    import pinecone
except ImportError:
    pinecone = None
    print("[WARN] Pinecone not installed. Install with: pip install pinecone-client")


class VectorDatabaseUploader:
    """Upload document repository to vector databases"""

    def __init__(self, repository_path: str = "PROJ344_document_repository"):
        """Initialize uploader"""

        self.repo_path = Path(repository_path)

        if not self.repo_path.exists():
            raise Exception(f"Repository not found: {repository_path}")

        # OpenAI for embeddings
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        if self.openai_key:
            openai.api_key = self.openai_key
        else:
            print("[WARN] OPENAI_API_KEY not set - embeddings will fail")

        # Qdrant setup
        self.qdrant_url = os.environ.get('QDRANT_URL', 'http://localhost:6333')
        self.qdrant_api_key = os.environ.get('QDRANT_API_KEY')

        if QdrantClient:
            try:
                if self.qdrant_api_key:
                    self.qdrant = QdrantClient(url=self.qdrant_url, api_key=self.qdrant_api_key)
                else:
                    self.qdrant = QdrantClient(url=self.qdrant_url)
                print(f"[OK] Qdrant client connected: {self.qdrant_url}")
            except Exception as e:
                self.qdrant = None
                print(f"[WARN] Qdrant connection failed: {e}")
        else:
            self.qdrant = None

        # Pinecone setup
        self.pinecone_api_key = os.environ.get('PINECONE_API_KEY')
        self.pinecone_env = os.environ.get('PINECONE_ENVIRONMENT', 'us-west1-gcp')

        if pinecone and self.pinecone_api_key:
            try:
                pinecone.init(api_key=self.pinecone_api_key, environment=self.pinecone_env)
                print(f"[OK] Pinecone initialized: {self.pinecone_env}")
                self.pinecone_client = pinecone
            except Exception as e:
                self.pinecone_client = None
                print(f"[WARN] Pinecone initialization failed: {e}")
        else:
            self.pinecone_client = None

    def generate_embedding(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """Generate embedding using OpenAI"""

        if not self.openai_key:
            raise Exception("OPENAI_API_KEY not set")

        # Truncate if too long (ada-002 supports ~8k tokens)
        max_chars = 30000
        if len(text) > max_chars:
            text = text[:max_chars]

        response = openai.Embedding.create(
            model=model,
            input=text
        )

        return response['data'][0]['embedding']

    def chunk_document(self, content: str, chunk_size: int = 1000, overlap: int = 200) -> List[Tuple[str, int]]:
        """Split document into overlapping chunks"""

        words = content.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            chunks.append((chunk_text, i))

        return chunks

    def upload_to_qdrant(self, collection_name: str = "proj344_documents"):
        """Upload documents to Qdrant with embeddings"""

        if not self.qdrant:
            print("[ERROR] Qdrant client not available")
            return

        print("=" * 80)
        print(f"UPLOADING TO QDRANT: {collection_name}")
        print("=" * 80)
        print()

        # Create collection if doesn't exist
        try:
            self.qdrant.get_collection(collection_name)
            print(f"[OK] Collection '{collection_name}' exists")
        except:
            print(f"[CREATE] Creating collection '{collection_name}'...")
            self.qdrant.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=1536,  # OpenAI ada-002 embedding size
                    distance=Distance.COSINE
                )
            )
            print(f"[OK] Collection created")

        print()

        # Load index
        index_file = self.repo_path / "document_index.json"
        with open(index_file) as f:
            index = json.load(f)

        uploaded = 0
        failed = 0

        for i, doc_info in enumerate(index['documents'], 1):
            if doc_info['status'] != 'success':
                continue

            # Load full document
            json_file = doc_info['saved_files']['json_file']
            with open(json_file) as f:
                full_doc = json.load(f)

            metadata = full_doc['metadata']

            try:
                print(f"[{i}/{len(index['documents'])}] Processing: {metadata['file_name']}")

                # Chunk document
                chunks = self.chunk_document(full_doc['content'])
                print(f"   Chunked into {len(chunks)} segments")

                points = []

                for chunk_idx, (chunk_text, word_offset) in enumerate(chunks):
                    # Generate embedding
                    embedding = self.generate_embedding(chunk_text)

                    # Create unique ID
                    point_id = hashlib.md5(
                        f"{metadata['file_hash']}_chunk_{chunk_idx}".encode()
                    ).hexdigest()

                    # Create point
                    point = PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            'file_name': metadata['file_name'],
                            'file_type': metadata['file_type'],
                            'file_hash': metadata['file_hash'],
                            'title': metadata.get('title'),
                            'chunk_index': chunk_idx,
                            'chunk_text': chunk_text[:500],  # Preview
                            'word_offset': word_offset,
                            'word_count': metadata.get('word_count'),
                            'extraction_method': metadata.get('extraction_method'),
                            'created_at': datetime.now().isoformat()
                        }
                    )

                    points.append(point)

                # Upload batch
                self.qdrant.upsert(
                    collection_name=collection_name,
                    points=points
                )

                print(f"   [OK] Uploaded {len(points)} chunks")
                uploaded += 1

            except Exception as e:
                print(f"   [FAIL] {e}")
                failed += 1

        print()
        print("=" * 80)
        print("QDRANT UPLOAD COMPLETE")
        print("=" * 80)
        print(f"Uploaded: {uploaded}")
        print(f"Failed: {failed}")
        print()

    def upload_to_pinecone(self, index_name: str = "proj344-documents"):
        """Upload documents to Pinecone with embeddings"""

        if not self.pinecone_client:
            print("[ERROR] Pinecone client not available")
            return

        print("=" * 80)
        print(f"UPLOADING TO PINECONE: {index_name}")
        print("=" * 80)
        print()

        # Create index if doesn't exist
        if index_name not in pinecone.list_indexes():
            print(f"[CREATE] Creating index '{index_name}'...")
            pinecone.create_index(
                name=index_name,
                dimension=1536,  # OpenAI ada-002
                metric='cosine'
            )
            print(f"[OK] Index created")
        else:
            print(f"[OK] Index '{index_name}' exists")

        # Connect to index
        index = pinecone.Index(index_name)
        print()

        # Load document index
        index_file = self.repo_path / "document_index.json"
        with open(index_file) as f:
            doc_index = json.load(f)

        uploaded = 0
        failed = 0

        for i, doc_info in enumerate(doc_index['documents'], 1):
            if doc_info['status'] != 'success':
                continue

            # Load full document
            json_file = doc_info['saved_files']['json_file']
            with open(json_file) as f:
                full_doc = json.load(f)

            metadata = full_doc['metadata']

            try:
                print(f"[{i}/{len(doc_index['documents'])}] Processing: {metadata['file_name']}")

                # Chunk document
                chunks = self.chunk_document(full_doc['content'])
                print(f"   Chunked into {len(chunks)} segments")

                vectors = []

                for chunk_idx, (chunk_text, word_offset) in enumerate(chunks):
                    # Generate embedding
                    embedding = self.generate_embedding(chunk_text)

                    # Create unique ID
                    vector_id = f"{metadata['file_hash']}_chunk_{chunk_idx}"

                    # Create vector
                    vectors.append((
                        vector_id,
                        embedding,
                        {
                            'file_name': metadata['file_name'],
                            'file_type': metadata['file_type'],
                            'file_hash': metadata['file_hash'],
                            'title': metadata.get('title', ''),
                            'chunk_index': chunk_idx,
                            'chunk_text': chunk_text[:500],
                            'word_offset': word_offset,
                            'word_count': metadata.get('word_count', 0),
                            'extraction_method': metadata.get('extraction_method', '')
                        }
                    ))

                # Upload batch (Pinecone supports batches of 100)
                batch_size = 100
                for j in range(0, len(vectors), batch_size):
                    batch = vectors[j:j + batch_size]
                    index.upsert(vectors=batch)

                print(f"   [OK] Uploaded {len(vectors)} chunks")
                uploaded += 1

            except Exception as e:
                print(f"   [FAIL] {e}")
                failed += 1

        print()
        print("=" * 80)
        print("PINECONE UPLOAD COMPLETE")
        print("=" * 80)
        print(f"Uploaded: {uploaded}")
        print(f"Failed: {failed}")
        print()

    def search_qdrant(self, query: str, collection_name: str = "proj344_documents", limit: int = 5):
        """Search Qdrant using semantic similarity"""

        if not self.qdrant:
            print("[ERROR] Qdrant client not available")
            return

        print("=" * 80)
        print(f"SEARCHING QDRANT: '{query}'")
        print("=" * 80)
        print()

        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Search
        results = self.qdrant.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit
        )

        print(f"Found {len(results)} results:")
        print()

        for i, result in enumerate(results, 1):
            print(f"{i}. {result.payload['file_name']} (Score: {result.score:.4f})")
            print(f"   Title: {result.payload.get('title', 'N/A')}")
            print(f"   Chunk: {result.payload['chunk_index']}")
            print(f"   Text: {result.payload['chunk_text'][:150]}...")
            print()

    def search_pinecone(self, query: str, index_name: str = "proj344-documents", limit: int = 5):
        """Search Pinecone using semantic similarity"""

        if not self.pinecone_client:
            print("[ERROR] Pinecone client not available")
            return

        print("=" * 80)
        print(f"SEARCHING PINECONE: '{query}'")
        print("=" * 80)
        print()

        # Connect to index
        index = pinecone.Index(index_name)

        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Search
        results = index.query(
            vector=query_embedding,
            top_k=limit,
            include_metadata=True
        )

        print(f"Found {len(results['matches'])} results:")
        print()

        for i, match in enumerate(results['matches'], 1):
            meta = match['metadata']
            print(f"{i}. {meta['file_name']} (Score: {match['score']:.4f})")
            print(f"   Title: {meta.get('title', 'N/A')}")
            print(f"   Chunk: {meta['chunk_index']}")
            print(f"   Text: {meta['chunk_text'][:150]}...")
            print()


def main():
    """Main entry point"""

    print("=" * 80)
    print("DOCUMENT REPOSITORY TO VECTOR DATABASES")
    print("=" * 80)
    print()
    print("Supported: Qdrant, Pinecone")
    print("Embedding Model: OpenAI text-embedding-ada-002 (1536 dimensions)")
    print()

    # Initialize uploader
    uploader = VectorDatabaseUploader()

    print("=" * 80)
    print("CONFIGURATION")
    print("=" * 80)
    print(f"Qdrant: {'Available' if uploader.qdrant else 'Not Available'}")
    print(f"Pinecone: {'Available' if uploader.pinecone_client else 'Not Available'}")
    print(f"OpenAI API: {'Configured' if uploader.openai_key else 'Not Configured'}")
    print()

    if not uploader.openai_key:
        print("[ERROR] OPENAI_API_KEY required for embeddings")
        print("Set with: export OPENAI_API_KEY='your-key'")
        return

    print("Options:")
    print("1. Upload to Qdrant")
    print("2. Upload to Pinecone")
    print("3. Upload to both")
    print("4. Search Qdrant")
    print("5. Search Pinecone")
    print()

    choice = input("Enter choice (1-5): ").strip()

    if choice == '1':
        if uploader.qdrant:
            uploader.upload_to_qdrant()
        else:
            print("[ERROR] Qdrant not available")

    elif choice == '2':
        if uploader.pinecone_client:
            uploader.upload_to_pinecone()
        else:
            print("[ERROR] Pinecone not available")

    elif choice == '3':
        if uploader.qdrant:
            print("[1/2] Uploading to Qdrant...")
            uploader.upload_to_qdrant()
        else:
            print("[SKIP] Qdrant not available")

        if uploader.pinecone_client:
            print("[2/2] Uploading to Pinecone...")
            uploader.upload_to_pinecone()
        else:
            print("[SKIP] Pinecone not available")

    elif choice == '4':
        if uploader.qdrant:
            query = input("Enter search query: ").strip()
            uploader.search_qdrant(query)
        else:
            print("[ERROR] Qdrant not available")

    elif choice == '5':
        if uploader.pinecone_client:
            query = input("Enter search query: ").strip()
            uploader.search_pinecone(query)
        else:
            print("[ERROR] Pinecone not available")

    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
