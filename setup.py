from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-logmaster",
    version="1.0.0",
    author="Divyansh",
    author_email="ry604492@gmail.com",
    description="Smart error analysis tool with AI-powered solutions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Divodude/ai-logmaster",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "langchain>=1.0.0",
        "langchain-community>=0.4.0",
        "langchain-core>=1.2.0",
        "langchain-openai>=1.0.0",
        "langgraph>=1.0.0",
        "duckduckgo-search>=8.0.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "requests>=2.32.0",
    ],
    extras_require={
        "rag": [
            "faiss-cpu>=1.13.0",
            "beautifulsoup4>=4.12.0",
            "lxml>=6.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "logmaster=ai_logmaster.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ai_logmaster": ["config/*.yaml", "config/*.example"],
    },
)
