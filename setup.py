from setuptools import setup, find_packages

setup(
    name="mac-sleep-timer",
    version="1.0.0",
    description="Интерактивный терминальный таймер сна для macOS",
    author="Mark",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "sleepmac = sleep_timer.cli:main",
        ],
    },
)
