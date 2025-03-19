import asyncio
import os
from server import (
    list_models,
    generate,
    GenerateParams,
    generate_from_file,
    GenerateFromFileParams,
    generate_from_url,
    GenerateFromUrlParams,
)
import logging

# Set up logging
logger = logging.getLogger(__name__)


async def test_list_models():
    """Test listing available models."""
    try:
        result = await list_models()
        print("\nAvailable Models:")
        for model in result["models"]:
            print(f"\nModel: {model['name']}")
            print(f"ID: {model['id']}")
            print(f"Description: {model['description']}")
            print(f"Input Format: {model['input_format']}")
            print(f"Output Format: {model['output_format']}")
            print(f"Capabilities: {model['capabilities']}")
        return result["models"]  # Return models for use in other tests
    except Exception as e:
        print(f"Error testing list_models: {e}")
        return []


async def test_generate():
    """Test text generation."""
    try:
        # Get available models
        models = await test_list_models()
        if not models:
            print("No models available for testing")
            return

        # Use the blog-post model for testing
        model_id = next(
            (m["id"] for m in models if m["name"] == "blog-post"), models[0]["id"]
        )

        params = GenerateParams(
            model=model_id,
            prompt="Write a short blog post about Python programming best practices",
        )
        result = await generate(params)
        print("\nGeneration Result:")
        print(result)
    except Exception as e:
        print(f"Error testing generate: {e}")


async def test_generate_from_file():
    """Test generation from file."""
    try:
        # Get available models
        models = await test_list_models()
        if not models:
            print("No models available for testing")
            return

        # Use the blog-post model for testing
        model_id = next(
            (m["id"] for m in models if m["name"] == "blog-post"), models[0]["id"]
        )

        # Test with blog post
        blog_params = GenerateFromFileParams(
            model=model_id, file_path="tests/data/blog_post.txt"
        )
        print("\nGenerating from blog post:")
        result = await generate_from_file(blog_params)
        print(result)

        # Test with technical doc
        tech_params = GenerateFromFileParams(
            model=model_id, file_path="tests/data/technical_doc.txt"
        )
        print("\nGenerating from technical doc:")
        result = await generate_from_file(tech_params)
        print(result)

    except Exception as e:
        print(f"Error testing generate_from_file: {e}")


async def test_generate_from_url():
    """Test generation from URL."""
    try:
        # Get available models
        models = await test_list_models()
        if not models:
            print("No models available for testing")
            return

        # Use the blog-post model for testing
        model_id = next(
            (m["id"] for m in models if m["name"] == "blog-post"), models[0]["id"]
        )

        # Test with a real URL
        web_params = GenerateFromUrlParams(
            model=model_id, url="https://python.org/about/", extract_article=True
        )
        print("\nGenerating from web URL:")
        result = await generate_from_url(web_params)
        print(result)

        # Test with another URL
        docs_params = GenerateFromUrlParams(
            model=model_id,
            url="https://docs.python.org/3/tutorial/introduction.html",
            extract_article=True,
        )
        print("\nGenerating from Python docs:")
        result = await generate_from_url(docs_params)
        print(result)

    except Exception as e:
        print(f"Error testing generate_from_url: {e}")


async def run_tests():
    """Run all tests."""
    await test_list_models()  # Called again by other tests
    await test_generate()
    await test_generate_from_file()
    await test_generate_from_url()


if __name__ == "__main__":
    asyncio.run(run_tests())
