from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="nutrition-recommender",
    version="1.0.0",
    author="Nutrition Recommender Contributors",
    author_email="your.email@example.com",
    description="Hybrid ML system for personalized nutrition recommendations targeting obesity management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nutrition-recommender",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Healthcare",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.0",
            "pytest-cov>=4.0",
            "black>=24.0",
            "flake8>=7.0",
            "mypy>=1.7",
            "sphinx>=7.0",
        ],
        "gpu": [
            "torch>=2.0",
            "tensorflow>=2.13",
        ],
    },
    entry_points={
        "console_scripts": [
            "nutrition-api=main:app",
            "nutrition-train=train_and_save_model:main",
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/nutrition-recommender/issues",
        "Documentation": "https://github.com/yourusername/nutrition-recommender/blob/main/README.md",
        "Source Code": "https://github.com/yourusername/nutrition-recommender",
    },
)
