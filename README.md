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
pip install -r requirements.txt
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

This will:

1. List all available Spiral models
2. Test the generation capability with a sample prompt

## MCP Tools

The server implements two MCP tools:

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

Example parameters:

```python
{
    "model": "model_id_or_slug",
    "prompt": "Your input text here"
}
```

## Error Handling

The server handles various error cases including:

- Invalid API key
- Model not found
- Input too long
- Server errors

## Environment Variables

- `SPIRAL_API_KEY`: Your Spiral API key (required)
- `PORT`: Server port (optional, defaults to 3000)
