# agents/marketing_agent/schemas.py

from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Tool Input Schemas
@dataclass
class ListPagesInput:
    business_id: str

@dataclass
class PostTextInput:
    business_id: str
    message: str

@dataclass
class PostImageInput:
    business_id: str
    caption: str
    image_url: str

# Tool Output Schemas
@dataclass
class PageInfo:
    id: str
    name: str
    category: str
    followers: int = 0
    likes: int = 0

@dataclass
class ListPagesOutput:
    success: bool
    pages: List[PageInfo]
    count: int
    error: Optional[str] = None

@dataclass
class PostOutput:
    success: bool
    post_id: Optional[str] = None
    message: Optional[str] = None
    page_name: Optional[str] = None
    error: Optional[str] = None

@dataclass
class PostImageOutput:
    success: bool
    post_id: Optional[str] = None
    message: Optional[str] = None
    page_name: Optional[str] = None
    image_url: Optional[str] = None
    error: Optional[str] = None

# Enum for tool types
class MarketingToolType(Enum):
    LIST_PAGES = "list_pages"
    POST_TEXT = "post_text"
    POST_IMAGE = "post_image"

# MCP Tool Schema Definitions
MCP_TOOL_SCHEMAS = {
    "list_pages": {
        "type": "object",
        "properties": {
            "business_id": {
                "type": "string",
                "description": "The business ID to get pages for"
            }
        },
        "required": ["business_id"]
    },
    "post_text": {
        "type": "object",
        "properties": {
            "business_id": {
                "type": "string",
                "description": "The business ID"
            },
            "message": {
                "type": "string",
                "description": "The text message to post to Facebook"
            }
        },
        "required": ["business_id", "message"]
    },
    "post_image": {
        "type": "object",
        "properties": {
            "business_id": {
                "type": "string",
                "description": "The business ID"
            },
            "caption": {
                "type": "string",
                "description": "Caption text for the image"
            },
            "image_url": {
                "type": "string",
                "description": "Public URL of the image to post"
            }
        },
        "required": ["business_id", "caption", "image_url"]
    }
}

# Tool descriptions for MCP
TOOL_DESCRIPTIONS = {
    "list_pages": "List all Facebook pages that the business has access to manage",
    "post_text": "Create a text post on the business's Facebook page",
    "post_image": "Create an image post with caption on the business's Facebook page"
}