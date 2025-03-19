# Spiral MCP Server

This is a Model Context Protocol (MCP) server implementation for the Spiral API using Python. It provides a standardized interface for interacting with Spiral's language models.

## Installation

```bash
mcp install src/server.py --name "spiral-writing-tool" --with pydantic --with requests --with beautifulsoup4 --with httpx
```

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

2. Install dependencies:

```bash
uv pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your Spiral API key:

```bash
SPIRAL_API_KEY=your_api_key_here
```

You can get your API key from https://app.spiral.computer/api

## Running the Server

Start the server:

```bash
python src/server.py
```

The server will run on port 3000 by default. You can change this by setting the `PORT` environment variable.

## Testing the Tools

To test the MCP tools directly:

```bash
python src/test_tools.py
```

This will run tests for all available tools to verify their functionality.

## MCP Tools

The server implements four powerful MCP tools:

### list_models

Lists all available Spiral models with their capabilities and metadata.

Example response:

```python
{
    "models": [
        {
            "id": "model-id",
            "name": "model-name",
            "description": "Model description",
            "input_format": "text",
            "output_format": "text",
            "capabilities": {
                "completion": true
            }
        }
    ]
}
```

### generate

Generates text using a specified Spiral model.

Parameters:
- `model`: The ID or slug of the Spiral model to use
- `prompt`: The input text to generate from

Example:
```python
{
    "model": "model_id_or_slug",
    "prompt": "Your input text here"
}
```

### generate_from_file

Generates text using a Spiral model with input from a file. This is useful for processing larger documents or maintaining consistent formatting.

Parameters:
- `model`: The ID or slug of the Spiral model to use
- `file_path`: Path to the file to use as input

Example:
```python
{
    "model": "model_id_or_slug",
    "file_path": "path/to/your/input.txt"
}
```

### generate_from_url

Generates text using a Spiral model with input from a URL. This tool can automatically extract article content from web pages.

Parameters:
- `model`: The ID or slug of the Spiral model to use
- `url`: URL to fetch content from
- `extract_article`: Whether to extract article content or use full HTML (default: true)

Example:
```python
{
    "model": "model_id_or_slug",
    "url": "https://example.com/article",
    "extract_article": true
}
```

## Error Handling

The server handles various error cases including:

- Invalid API key
- Model not found
- Input too long
- Rate limit exceeded
- URL fetch failures
- File read errors
- Server errors
- Request timeouts

Each error returns a clear error message to help diagnose the issue.

## Environment Variables

- `SPIRAL_API_KEY`: Your Spiral API key (required)
- `PORT`: Server port (optional, defaults to 3000)
- `TIMEOUT`: Request timeout in seconds (optional, defaults to 30)

## Features

- **Robust Error Handling**: Comprehensive error handling and logging for all operations
- **Article Extraction**: Smart extraction of article content from web pages
- **Flexible Input Sources**: Support for text, files, and URLs as input
- **Async Operations**: All operations are asynchronous for better performance
- **Type Safety**: Full Pydantic type validation for all parameters
- **Logging**: Detailed debug logging for troubleshooting
