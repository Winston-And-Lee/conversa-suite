import os
import logging
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional

from src.domain.repository.file_repository import IFileRepository
from src.config.settings import get_settings

logger = logging.getLogger(__name__)

class S3FileRepository(IFileRepository):
    """Implementation of file repository using AWS S3"""
    
    def __init__(self):
        """Initialize the S3 repository with AWS credentials"""
        # Get settings from configuration
        settings = get_settings()
        
        self.aws_access_key = settings.AWS_ACCESS_KEY_ID
        self.aws_secret_key = settings.AWS_SECRET_ACCESS_KEY
        self.aws_region = settings.AWS_REGION
        self.bucket_name = settings.S3_BUCKET_NAME
        
        if not all([self.aws_access_key, self.aws_secret_key, self.aws_region, self.bucket_name]):
            logger.warning("Missing AWS S3 configuration, some features may not work")
        
        # Initialize S3 client
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
        )
    
    async def upload(self, file_name: str, folder_path: str, file_data: bytes) -> Dict[str, Any]:
        """
        Upload a file to S3
        
        Args:
            file_name: Name of the file
            folder_path: Path to store the file
            file_data: Binary data of the file
            
        Returns:
            Dict containing file information including URL
        """
        # Combine folder path and file name
        full_path = f"{folder_path}/{file_name}" if folder_path else file_name
        
        # Determine content type based on file extension
        content_type = self._get_content_type(file_name)
        
        try:
            # Upload to S3
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=full_path,
                Body=file_data,
                ContentType=content_type
            )
            
            # Generate public URL
            file_url = f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{full_path}"
            
            return {
                "URL": file_url,
                "FileName": file_name,
                "FilePath": full_path,
                "FileSize": len(file_data)
            }
            
        except ClientError as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    async def get(self, file_name: str) -> bytes:
        """
        Get a file from S3
        
        Args:
            file_name: Name of the file to retrieve
            
        Returns:
            Binary data of the file
        """
        try:
            response = self.s3.get_object(
                Bucket=self.bucket_name,
                Key=file_name
            )
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"S3 get error: {str(e)}")
            raise Exception(f"Failed to get file: {str(e)}")
    
    async def delete(self, file_name: str) -> bool:
        """
        Delete a file from S3
        
        Args:
            file_name: Name of the file to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            self.s3.delete_object(
                Bucket=self.bucket_name,
                Key=file_name
            )
            return True
        except ClientError as e:
            logger.error(f"S3 delete error: {str(e)}")
            return False
    
    def _get_content_type(self, file_name: str) -> str:
        """
        Determine content type based on file extension
        
        Args:
            file_name: Name of the file
            
        Returns:
            Content type string
        """
        extension = file_name.split('.')[-1].lower()
        content_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'tiff': 'image/tiff',
            'tif': 'image/tiff',
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'csv': 'text/csv',
            'mp3': 'audio/mpeg',
            'mp4': 'video/mp4',
            'ico': 'image/x-icon'
        }
        return content_types.get(extension, 'application/octet-stream') 