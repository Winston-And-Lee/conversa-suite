---
title: Technical Reference
description: Technical reference for Conversa-Suite implementation
---

# Conversa-Suite Technical Reference

This section contains technical reference documentation for the Conversa-Suite platform, including architecture details, code organization, and implementation guidelines.

## Architecture

- [Backend Architecture](./backend-architecture) - Overview of the backend architecture and patterns
- [Data Ingestion Module](./data-ingestion) - Detailed documentation of the Data Ingestion module

## Domain Entities

- User Entity - Core user data structure and behavior
- Authentication - Token generation, validation, and security practices
- Data Ingestion - Thai legal data ingestion and search functionality

## Implementation Details

- Clean Architecture - How the codebase follows clean architecture principles
- Repository Pattern - Data access implementation
- Dependency Injection - How dependencies are managed in the application

## Technology Stack

- FastAPI - Web framework for building APIs
- MongoDB - Document database for data storage
- AWS S3 - Storage for file uploads
- Pinecone - Vector database for semantic search
- OpenAI - AI services for embeddings and keyword generation
- JWT - Token-based authentication mechanism
- Postmark - Email delivery service for user communications 