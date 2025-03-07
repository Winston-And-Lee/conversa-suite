import os
import uuid
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException


class S3Repository:
    """Repository for interacting with AWS S3."""

    def __init__(self):
        """Initialize the S3 repository with AWS credentials."""
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION")
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        
        if not all([self.aws_access_key, self.aws_secret_key, self.aws_region, self.bucket_name]):
            raise ValueError("Missing AWS S3 configuration")
        
        # Initialize S3 client
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
        )
    
    async def upload_file(self, file: UploadFile) -> dict:
        """
        Upload a file to S3.
        
        Args:
            file: The file to upload
            
        Returns:
            dict: Dictionary containing file URL, name, type, and size
        """
        # Check file type (PDF or DOC/DOCX only)
        file_type = file.content_type
        if file_type not in ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            raise HTTPException(status_code=400, detail="Only PDF and DOC/DOCX files are allowed")
        
        # Check file size (max 10MB)
        await file.seek(0)
        file_data = await file.read()
        file_size = len(file_data)
        
        if file_size > 10 * 1024 * 1024:  # 10MB in bytes
            raise HTTPException(status_code=400, detail="File size exceeds maximum of 10MB")
        
        # Generate unique filename
        original_filename = file.filename
        file_extension = original_filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Upload to S3
        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_data,
                ContentType=file_type
            )
            
            # Generate public URL
            file_url = f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{unique_filename}"
            
            return {
                "file_url": file_url,
                "file_name": original_filename,
                "file_type": file_type,
                "file_size": file_size
            }
            
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"S3 upload error: {str(e)}")
        
    async def delete_file(self, file_url: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            file_url: The URL of the file to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        # Extract key from URL
        key = file_url.split("/")[-1]
        
        try:
            self.s3.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
        except ClientError:
            return False 