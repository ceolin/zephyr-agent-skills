#!/usr/bin/env python3
import json
import re
from pathlib import Path


def read_frontmatter_description(skill_md: Path) -> str:
    """Extract the description field from a SKILL.md YAML frontmatter block."""
    try:
        content = skill_md.read_text(encoding="utf-8")
        # Match the first YAML frontmatter block
        match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if match:
            fm = match.group(1)
            desc_match = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
            if desc_match:
                return desc_match.group(1).strip()
    except OSError:
        pass
    return ""


def generate_marketplace():
    # Define paths
    repo_root = Path(__file__).parent.parent
    skills_dir = repo_root / "skills"
    output_dir = repo_root / ".claude-plugin"
    output_file = output_dir / "marketplace.json"

    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)

    # Root umbrella skill description (from repo-root SKILL.md)
    root_description = read_frontmatter_description(repo_root / "SKILL.md")

    # Build plugins array — root entry first, then skills sorted for deterministic output
    plugins = [
        {
            "name": "zephyr-skills",
            # source is relative to metadata.pluginRoot (./skills relative to .claude-plugin/)
            # ".." resolves to the repo root
            "source": "..",
            "description": root_description,
        }
    ]

    if skills_dir.exists():
        for item in sorted(skills_dir.iterdir(), key=lambda p: p.name):
            if item.is_dir() and (item / "SKILL.md").exists():
                skill_name = item.name
                description = read_frontmatter_description(item / "SKILL.md")
                plugins.append(
                    {
                        "name": skill_name,
                        # source paths are relative to metadata.pluginRoot ("./skills")
                        "source": f"./{skill_name}",
                        "description": description,
                    }
                )

    marketplace = {
        "name": "zephyr-agent-skills",
        "owner": {
            "name": "beriberikix"
        },
        "description": "A registry of professional, agent-ready skills for building with Zephyr RTOS",
        "version": "1.0.0",
        "$schema": "https://code.claude.com/schemas/marketplace.json",
        "metadata": {
            "pluginRoot": "./skills"
        },
        "plugins": plugins,
    }

    # Write JSON file
    with open(output_file, "w") as f:
        json.dump(marketplace, f, indent=2)
        f.write("\n")  # Trailing newline

    print(f"Generated marketplace.json at {output_file}")
    print(f"Total plugins: {len(marketplace['plugins'])}")


if __name__ == "__main__":
    generate_marketplace()
