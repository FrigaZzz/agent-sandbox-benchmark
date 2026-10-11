"""Compatibility entry point; use the same evidence engine as the CLI/dashboard."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.bench.leaderboard import calculate_leaderboard, generate_markdown_report

if __name__ == "__main__":
    print(generate_markdown_report(calculate_leaderboard()))
