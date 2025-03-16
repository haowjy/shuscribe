# shuscribe/tasks/llm_tasks.py

from typing import Any, Dict, List, Optional
from celery import shared_task
import httpx
import json
import asyncio
import logging

from shuscribe.services.llm.providers.provider import Message
from shuscribe.services.llm.session import LLMSession

logger = logging.getLogger(__name__)
