"""
Google Drive Sync Module
Handles listing and downloading documents from 7TB Google Drive storage
"""

import os
import io
import logging
from typing import List, Dict, Optional, Any, Generator
from dataclasses import dataclass
from pathlib import Path
import json
import hashlib

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


@dataclass
class GoogleDriveDocument:
    """Represents a document in Google Drive"""
    id: str
    name: str
    mime_type: str
    size: int
    created_time: str
    modified_time: str
    parents: List[str]
    web_view_link: str
    drive_path: Optional[str] = None
    is_processed: bool = False


class GoogleDriveSync:
    """
    Google Drive synchronization client

    Handles authentication, listing, and downloading documents from
    7TB Google Drive storage for batch processing.

    Features:
    - OAuth2 authentication
    - Recursive folder traversal
    - Selective sync by file type
    - Exclude already processed documents
    - Progress tracking
    - Resume capability
    """

    def __init__(
        self,
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
        cache_path: str = "drive_cache.json"
    ):
        """
        Initialize Google Drive sync client

        Args:
            credentials_path: Path to Google OAuth2 credentials JSON
            token_path: Path to store access token
            cache_path: Path to cache document listings
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.cache_path = cache_path

        self.service = None
        self.document_cache: Dict[str, GoogleDriveDocument] = {}

        logger.info("✅ Google Drive sync initialized")

    def authenticate(self) -> None:
        """
        Authenticate with Google Drive API using OAuth2

        Creates a token.json file to store credentials for future runs.
        If credentials expire, will automatically refresh.
        """
        logger.info("🔐 Authenticating with Google Drive...")

        creds = None

        # Load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("🔄 Refreshing expired credentials...")
                creds.refresh(Request())
            else:
                logger.info("🌐 Starting OAuth2 flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
            logger.info(f"✅ Credentials saved to {self.token_path}")

        # Build Drive API service
        self.service = build('drive', 'v3', credentials=creds)

        logger.info("✅ Google Drive authentication successful")

    def list_documents(
        self,
        folder_id: Optional[str] = None,
        mime_types: Optional[List[str]] = None,
        max_results: Optional[int] = None,
        recursive: bool = True
    ) -> List[GoogleDriveDocument]:
        """
        List documents in Google Drive

        Args:
            folder_id: Specific folder ID (None = root)
            mime_types: Filter by MIME types (e.g., ['application/pdf'])
            max_results: Maximum documents to return
            recursive: Recursively scan subfolders

        Returns:
            List of GoogleDriveDocument objects
        """
        if not self.service:
            raise RuntimeError("Must authenticate before listing documents")

        logger.info(f"📋 Listing documents from Google Drive...")

        documents = []

        # Build query
        query_parts = []

        if folder_id:
            query_parts.append(f"'{folder_id}' in parents")

        if mime_types:
            mime_query = " or ".join([f"mimeType='{mt}'" for mt in mime_types])
            query_parts.append(f"({mime_query})")

        # Exclude trashed files
        query_parts.append("trashed=false")

        query = " and ".join(query_parts)

        # List files
        page_token = None
        total_fetched = 0

        try:
            while True:
                response = self.service.files().list(
                    q=query,
                    spaces='drive',
                    fields='nextPageToken, files(id, name, mimeType, size, createdTime, '
                           'modifiedTime, parents, webViewLink)',
                    pageToken=page_token,
                    pageSize=1000  # Max per page
                ).execute()

                files = response.get('files', [])

                for file_data in files:
                    # Skip folders if we're looking for documents
                    if file_data['mimeType'] == 'application/vnd.google-apps.folder':
                        if recursive:
                            # Recursively scan this folder
                            subfolder_docs = self.list_documents(
                                folder_id=file_data['id'],
                                mime_types=mime_types,
                                max_results=max_results - total_fetched if max_results else None,
                                recursive=True
                            )
                            documents.extend(subfolder_docs)
                            total_fetched += len(subfolder_docs)
                        continue

                    # Create document object
                    doc = GoogleDriveDocument(
                        id=file_data['id'],
                        name=file_data['name'],
                        mime_type=file_data['mimeType'],
                        size=int(file_data.get('size', 0)),
                        created_time=file_data['createdTime'],
                        modified_time=file_data['modifiedTime'],
                        parents=file_data.get('parents', []),
                        web_view_link=file_data.get('webViewLink', '')
                    )

                    documents.append(doc)
                    self.document_cache[doc.id] = doc
                    total_fetched += 1

                    if max_results and total_fetched >= max_results:
                        break

                if max_results and total_fetched >= max_results:
                    break

                page_token = response.get('nextPageToken')
                if not page_token:
                    break

        except HttpError as error:
            logger.error(f"❌ Error listing documents: {error}")
            raise

        logger.info(f"✅ Found {len(documents)} documents")

        # Save cache
        self._save_cache()

        return documents

    def filter_unprocessed(
        self,
        documents: List[GoogleDriveDocument],
        processed_ids: List[str]
    ) -> List[GoogleDriveDocument]:
        """
        Filter out already processed documents

        Args:
            documents: List of all documents
            processed_ids: List of document IDs already processed

        Returns:
            Filtered list of unprocessed documents
        """
        processed_set = set(processed_ids)

        unprocessed = [
            doc for doc in documents
            if doc.id not in processed_set
        ]

        logger.info(f"📊 {len(documents)} total documents, {len(unprocessed)} unprocessed")

        return unprocessed

    def create_batches(
        self,
        documents: List[GoogleDriveDocument],
        batch_size: int = 100
    ) -> List[List[GoogleDriveDocument]]:
        """
        Split documents into batches for processing

        Args:
            documents: List of documents
            batch_size: Documents per batch

        Returns:
            List of batches (each batch is a list of documents)
        """
        batches = []

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batches.append(batch)

        logger.info(f"📦 Created {len(batches)} batches of up to {batch_size} documents")

        return batches

    def download_document(
        self,
        document_id: str,
        output_path: str
    ) -> bool:
        """
        Download a document from Google Drive

        Args:
            document_id: Google Drive document ID
            output_path: Local path to save document

        Returns:
            True if download successful
        """
        if not self.service:
            raise RuntimeError("Must authenticate before downloading")

        try:
            request = self.service.files().get_media(fileId=document_id)

            with io.FileIO(output_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False

                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        logger.debug(f"Download {int(status.progress() * 100)}% complete")

            logger.debug(f"✅ Downloaded {document_id} to {output_path}")
            return True

        except HttpError as error:
            logger.error(f"❌ Error downloading {document_id}: {error}")
            return False

    def download_batch(
        self,
        documents: List[GoogleDriveDocument],
        output_dir: str
    ) -> List[str]:
        """
        Download a batch of documents

        Args:
            documents: List of documents to download
            output_dir: Directory to save documents

        Returns:
            List of successfully downloaded file paths
        """
        logger.info(f"⬇️ Downloading batch of {len(documents)} documents...")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        downloaded_paths = []

        for doc in documents:
            # Create safe filename
            safe_name = self._sanitize_filename(doc.name)
            file_path = output_path / f"{doc.id}_{safe_name}"

            if self.download_document(doc.id, str(file_path)):
                downloaded_paths.append(str(file_path))

        logger.info(f"✅ Downloaded {len(downloaded_paths)} / {len(documents)} documents")

        return downloaded_paths

    def get_document_metadata(self, document_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific document

        Args:
            document_id: Google Drive document ID

        Returns:
            Document metadata
        """
        if not self.service:
            raise RuntimeError("Must authenticate before accessing metadata")

        try:
            file = self.service.files().get(
                fileId=document_id,
                fields='id, name, mimeType, size, createdTime, modifiedTime, '
                       'parents, webViewLink, description, properties'
            ).execute()

            return file

        except HttpError as error:
            logger.error(f"❌ Error getting metadata for {document_id}: {error}")
            raise

    def estimate_storage_size(self, documents: List[GoogleDriveDocument]) -> Dict[str, Any]:
        """
        Calculate total storage size for documents

        Args:
            documents: List of documents

        Returns:
            Storage size breakdown
        """
        total_bytes = sum(doc.size for doc in documents)

        size_breakdown = {
            "total_documents": len(documents),
            "total_bytes": total_bytes,
            "total_mb": round(total_bytes / (1024 * 1024), 2),
            "total_gb": round(total_bytes / (1024 * 1024 * 1024), 2),
            "total_tb": round(total_bytes / (1024 * 1024 * 1024 * 1024), 2),
            "average_size_mb": round((total_bytes / len(documents)) / (1024 * 1024), 2) if documents else 0
        }

        logger.info(f"📊 Storage estimate: {size_breakdown['total_tb']} TB across {len(documents)} documents")

        return size_breakdown

    def _sanitize_filename(self, filename: str) -> str:
        """
        Create safe filename by removing problematic characters

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove problematic characters
        safe = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-'))
        safe = safe.strip()

        # Limit length
        if len(safe) > 200:
            name, ext = os.path.splitext(safe)
            safe = name[:200] + ext

        return safe

    def _save_cache(self) -> None:
        """Save document cache to disk"""
        try:
            cache_data = {
                doc_id: {
                    "id": doc.id,
                    "name": doc.name,
                    "mime_type": doc.mime_type,
                    "size": doc.size,
                    "created_time": doc.created_time,
                    "modified_time": doc.modified_time,
                    "parents": doc.parents,
                    "web_view_link": doc.web_view_link,
                    "is_processed": doc.is_processed
                }
                for doc_id, doc in self.document_cache.items()
            }

            with open(self.cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)

            logger.debug(f"💾 Cache saved to {self.cache_path}")

        except Exception as e:
            logger.error(f"❌ Error saving cache: {e}")

    def _load_cache(self) -> None:
        """Load document cache from disk"""
        if not os.path.exists(self.cache_path):
            return

        try:
            with open(self.cache_path, 'r') as f:
                cache_data = json.load(f)

            for doc_id, doc_dict in cache_data.items():
                self.document_cache[doc_id] = GoogleDriveDocument(**doc_dict)

            logger.debug(f"💾 Cache loaded from {self.cache_path}")

        except Exception as e:
            logger.error(f"❌ Error loading cache: {e}")


if __name__ == "__main__":
    """
    Test Google Drive sync

    Usage:
        python google_drive_sync.py

    Prerequisites:
        1. Create Google Cloud project
        2. Enable Google Drive API
        3. Create OAuth2 credentials
        4. Download credentials.json to this directory
    """

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize client
    sync = GoogleDriveSync()

    # Authenticate
    try:
        sync.authenticate()
    except FileNotFoundError:
        print("\n❌ ERROR: credentials.json not found!")
        print("\nTo set up Google Drive API:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project")
        print("3. Enable Google Drive API")
        print("4. Create OAuth2 credentials")
        print("5. Download credentials.json")
        print("6. Place credentials.json in batch-processor/ directory")
        exit(1)

    # List PDF documents
    print("\n📋 Listing PDF documents in Google Drive...")
    documents = sync.list_documents(
        mime_types=['application/pdf'],
        max_results=100,  # Limit to 100 for testing
        recursive=True
    )

    if documents:
        print(f"\n✅ Found {len(documents)} PDF documents:")

        # Show first 10
        for i, doc in enumerate(documents[:10]):
            print(f"\n{i+1}. {doc.name}")
            print(f"   ID: {doc.id}")
            print(f"   Size: {doc.size / (1024*1024):.2f} MB")
            print(f"   Modified: {doc.modified_time}")

        # Estimate storage
        print("\n📊 Storage Estimate:")
        estimate = sync.estimate_storage_size(documents)
        print(f"   Total Documents: {estimate['total_documents']:,}")
        print(f"   Total Size: {estimate['total_gb']:.2f} GB ({estimate['total_tb']:.2f} TB)")
        print(f"   Average Size: {estimate['average_size_mb']:.2f} MB")

        # Create batches
        print("\n📦 Creating batches...")
        batches = sync.create_batches(documents, batch_size=100)
        print(f"   Total Batches: {len(batches)}")
        print(f"   Batch Size: 100 documents")

    else:
        print("\n⚠️ No PDF documents found")
