from setuptools import setup
import py2exe

setup(
    windows=[{
        "script": "src/main.py",  # Entry point of your application
        "icon_resources": [(1, "assets/app_icon.ico")],  # Optional: Add an icon
    }],
    options={
        "py2exe": {
            "includes": ["PyQt6"],  # Include required packages
            "bundle_files": 1,  # Bundle everything into one file
            "compressed": True,  # Compress the executable
        }
    },
    zipfile=None,  # Include everything in the executable
)