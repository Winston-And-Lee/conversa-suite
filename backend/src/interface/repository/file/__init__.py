from src.interface.repository.file.file_repository import S3FileRepository

def FileRepository():
    """Factory function to create a file repository instance"""
    return S3FileRepository() 