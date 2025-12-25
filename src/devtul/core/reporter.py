import http.server
import json
import os
import socketserver
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict

import git
import typer
from jinja2 import Environment, FileSystemLoader

from devtul.core.config import JINJA_ENVIRONMENT
from devtul.core.file_utils import (GitScanModes,
                                    filter_gathered_paths_dy_default_ignores,
                                    gather_all_paths,
                                    try_gather_all_git_tracked_paths)
from devtul.core.models import FileResult
from devtul.git.utils import get_file_git_history, get_git_metadata

app = typer.Typer(
    name="reporter",
    help="Generate and serve HTML reports from scanned file data.",
)

CACHE_FILE = ".devtul_cache.json"
REPORT_DIR = "htmlcov_devtul"


@app.command()
def scan(
    path: Path = typer.Argument(..., help="Root directory to scan"),
    mode: GitScanModes = typer.Option(GitScanModes.ALL_FILES, help="Scan mode"),
    output: Path = typer.Option(Path(CACHE_FILE), help="Output cache file"),
):
    """
    Scans files using FileResult models and generates a JSON cache.
    """
    abs_root = path.resolve()

    # 1. Gather Paths
    if mode == GitScanModes.GIT_TRACKED:
        raw_paths = try_gather_all_git_tracked_paths(abs_root)
    else:
        raw_paths = gather_all_paths(abs_root)

    # 2. Filter
    filtered_paths = filter_gathered_paths_dy_default_ignores(raw_paths)

    # 3. Build Data
    results = []
    repo = None
    repo_meta = None

    # Try to init git repo object if available
    if (abs_root / ".git").exists():
        try:
            repo = git.Repo(abs_root)
            # Use your git_utils function to get metadata
            repo_meta = get_git_metadata(abs_root)
        except Exception:
            pass

    with typer.progressbar(filtered_paths, label="Indexing Files") as progress:
        for p in progress:
            if not p.is_file():
                continue

            f_res = FileResult(file_path=p, input_path=abs_root)

            # Add filesystem events
            if f_res.created_at:
                f_res.events.append(
                    {
                        "type": "created",
                        "date": f_res.created_at.isoformat(),
                        "message": "File Created (FS)",
                        "author": "System",
                    }
                )

            if f_res.modified_at:
                f_res.events.append(
                    {
                        "type": "modified",
                        "date": f_res.modified_at.isoformat(),
                        "message": "File Modified (FS)",
                        "author": "System",
                    }
                )

            # Add Git events if applicable
            if repo and mode == GitScanModes.GIT_TRACKED:
                # We need relative path for git query
                try:
                    rel_path = p.relative_to(abs_root)
                    git_events = get_file_git_history(repo, rel_path)
                    f_res.events.extend(git_events)
                except Exception:
                    pass

            results.append(f_res.to_dict())

    # 4. Construct Final Cache Object
    # We serialize the GitMetadata model to dict if it exists
    git_meta_dict = repo_meta.model_dump() if repo_meta else None

    cache_data = {
        "generated_at": datetime.now().isoformat(),
        "root": str(abs_root),
        "mode": mode.value,
        "git_metadata": git_meta_dict,
        "files": results,
    }

    # Write Cache
    with open(output, "w") as f:
        json.dump(cache_data, f, indent=2)

    # Generate HTML immediately
    generate_report(cache_data)


def generate_report(data: Dict):
    """Generates the HTML report from the cache data."""
    env = JINJA_ENVIRONMENT
    template = env.get_template("report.html")

    # Create output directory
    out_dir = Path(REPORT_DIR)
    out_dir.mkdir(exist_ok=True)

    # Copy static assets if you have them (css/js), otherwise we use CDN in template

    html_out = template.render(data=json.dumps(data))

    index_path = out_dir / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    typer.echo(f"Report generated: {index_path}")


@app.command()
def serve(port: int = 9099):
    """Serves the generated report."""
    os.chdir(REPORT_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    url = f"http://localhost:{port}"
    typer.echo(f"Serving at {url}")
    webbrowser.open(url)
    with socketserver.TCPServer(("", port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    app()
