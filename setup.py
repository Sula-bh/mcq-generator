from setuptools import setup, find_packages

setup(
    name="mcqgenerator",
    version="0.0.1",
    author="Sulabh Acharya",
    author_email="sulava06@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "langchain-google-genai",
        "langchain",
        "streamlit",
        "python-dotenv",
        "PyPDF2",
    ]
)
