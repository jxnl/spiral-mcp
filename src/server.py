from typing import Optional
import os
from dotenv import load_dotenv
import httpx
from pydantic import BaseModel, Field
import logging
from bs4 import BeautifulSoup
import re

from mcp.server.fastmcp import FastMCP, Context

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

SPIRAL_API_KEY = os.getenv("SPIRAL_API_KEY")
BASE_URL = "https://app.spiral.computer/api/v1"
TIMEOUT = 30.0  # 30 seconds timeout

if not SPIRAL_API_KEY:
    raise ValueError("SPIRAL_API_KEY environment variable is required")

# Create MCP server
mcp = FastMCP(
    "Spiral API", dependencies=["requests", "python-dotenv", "pydantic", "httpx"]
)


# Model definitions
class GenerateParams(BaseModel):
    model: str = Field(..., description="The ID or slug of the Spiral model to use")
    prompt: str = Field(..., description="The input text to generate from")


class GenerateFromFileParams(BaseModel):
    model: str = Field(..., description="The ID or slug of the Spiral model to use")
    file_path: str = Field(..., description="Path to the file to use as input")


class GenerateFromUrlParams(BaseModel):
    model: str = Field(..., description="The ID or slug of the Spiral model to use")
    url: str = Field(..., description="URL to fetch content from")
    extract_article: bool = Field(
        True, description="Whether to extract article content or use full HTML"
    )


def extract_article_content(html: str) -> str:
    """Extract clean article content from HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted elements
    for element in soup.find_all(["script", "style", "nav", "footer", "iframe"]):
        element.decompose()

    # Try to find article content
    article = None

    # Check for article tag first
    if soup.find("article"):
        article = soup.find("article")
    # Then try main tag
    elif soup.find("main"):
        article = soup.find("main")
    # Look for common article content class names
    elif soup.find(class_=re.compile(r"article|post|content|entry")):
        article = soup.find(class_=re.compile(r"article|post|content|entry"))
    else:
        # Fallback to body
        article = soup.find("body")

    if not article:
        return soup.get_text(separator="\n", strip=True)

    # Extract text with structure preservation
    content = []
    for element in article.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
        text = element.get_text(strip=True)
        if text:
            if element.name.startswith("h"):
                content.append(f"\n{'#' * int(element.name[1])} {text}\n")
            elif element.name == "li":
                content.append(f"- {text}")
            else:
                content.append(text)

    return "\n\n".join(content)


@mcp.tool()
async def list_models() -> dict:
    """List available Spiral models with their capabilities."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{BASE_URL}/spirals",
                headers={
                    "x-api-key": SPIRAL_API_KEY,
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()

            models = [
                {
                    "id": spiral["id"],
                    "name": spiral.get("slug", spiral["id"]),
                    "description": spiral.get("text_summary"),
                    "input_format": spiral.get("inputFormat"),
                    "output_format": spiral.get("outputFormat"),
                    "capabilities": {"completion": True},
                }
                for spiral in response.json()["spirals"]
            ]

            return {"models": models}
    except httpx.TimeoutException:
        raise ValueError("Request timed out while listing models")
    except httpx.HTTPError as e:
        raise ValueError(f"Failed to list models: {str(e)}")


@mcp.tool()
async def generate(params: GenerateParams) -> str:
    """Generate text using a Spiral model."""
    try:
        logger.debug(
            f"Generating with model {params.model} and prompt: {params.prompt}"
        )
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/spirals/{params.model}/generate",
                json={"input": params.prompt},
                headers={
                    "x-api-key": SPIRAL_API_KEY,
                    "Content-Type": "application/json",
                },
            )

            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            logger.debug(f"Response body: {response.text}")

            if response.status_code == 404:
                raise ValueError(f"Model '{params.model}' not found")
            if response.status_code == 413:
                raise ValueError("Input too long")
            if response.status_code == 401:
                raise ValueError("Invalid API key")
            if response.status_code == 429:
                raise ValueError("Rate limit exceeded")

            response.raise_for_status()
            result = response.json()

            if "output" not in result:
                raise ValueError(f"Unexpected response format: {result}")

            return result["output"]
    except httpx.TimeoutException:
        logger.error("Request timed out during generation")
        raise ValueError("Request timed out during generation")
    except httpx.HTTPError as e:
        logger.error(f"HTTP error during generation: {str(e)}")
        raise ValueError(f"Failed to generate: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during generation: {str(e)}")
        raise ValueError(f"Failed to generate: {str(e)}")


@mcp.tool()
async def generate_from_file(params: GenerateFromFileParams) -> str:
    """Generate text using a Spiral model with input from a file."""
    try:
        # Read the file content
        try:
            with open(params.file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
        except FileNotFoundError:
            raise ValueError(f"File not found: {params.file_path}")
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")

        logger.debug(f"Read {len(file_content)} characters from {params.file_path}")

        # Use the generate function with file content
        gen_params = GenerateParams(model=params.model, prompt=file_content)
        return await generate(gen_params)

    except Exception as e:
        logger.error(f"Error in generate_from_file: {str(e)}")
        raise ValueError(f"Failed to generate from file: {str(e)}")


@mcp.tool()
async def generate_from_url(params: GenerateFromUrlParams) -> str:
    """Generate text using a Spiral model with input from a URL."""
    try:
        logger.debug(f"Fetching content from URL: {params.url}")
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(params.url)
            response.raise_for_status()

            html_content = response.text

            if params.extract_article:
                content = extract_article_content(html_content)
                logger.debug(f"Extracted {len(content)} characters of article content")
            else:
                content = html_content
                logger.debug(f"Using full HTML content: {len(content)} characters")

        # Use the generate function with the extracted content
        gen_params = GenerateParams(model=params.model, prompt=content)
        return await generate(gen_params)

    except httpx.TimeoutException:
        raise ValueError(f"Request timed out while fetching URL: {params.url}")
    except httpx.HTTPError as e:
        raise ValueError(f"Failed to fetch URL {params.url}: {str(e)}")
    except Exception as e:
        logger.error(f"Error in generate_from_url: {str(e)}")
        raise ValueError(f"Failed to generate from URL: {str(e)}")


if __name__ == "__main__":
    mcp.run()
