"""Setup script for OmniSight AI."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="omnisight-ai",
    version="2.0.0",
    description="Advanced Open-Source Intelligence (OSINT) Tool with Groq AI Integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ali Zafar",
    author_email="",
    url="https://github.com/AliZafar780/ai-osint-tool",
    packages=find_packages(),
    py_modules=["advanced_osint_tool", "osint_gui"],
    install_requires=[
        "requests>=2.28.0",
        "colorama>=0.4.6",
        "dnspython>=2.3.0",
        "pyyaml>=6.0",
        "Pillow>=9.0.0",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "dashboard": ["fastapi>=0.104.0", "uvicorn>=0.24.0"],
        "ai": ["groq>=0.5.0"],
        "pdf": ["weasyprint>=60.0"],
        "all": ["fastapi>=0.104.0", "uvicorn>=0.24.0", "groq>=0.5.0"],
    },
    entry_points={
        "console_scripts": [
            "omnisight=advanced_osint_tool:main",
            "omnisight-dashboard=dashboard.app:run_dashboard",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.8",
)
