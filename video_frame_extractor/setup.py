from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="video-frame-extractor",
    use_scm_version=False,
    version="1.0.0",
    author="Paul Chibueze",
    author_email="chibuezedeveloper@gmail.com",
    description="A Python library for downloading videos and extracting frames at specified intervals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chibuezedev/video-frame-extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "video-extractor=video_frame_extractor.cli:main",
        ],
    },
    keywords="video, frame extraction, opencv, multimedia, video processing",
    project_urls={
        "Bug Reports": "https://github.com/chibuezedev/video-frame-extractor/issues",
        "Source": "https://github.com/chibuezedev/video-frame-extractor",
        "Documentation": "https://github.com/chibuezedev/video-frame-extractor#readme",
    },
)
