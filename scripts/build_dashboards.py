#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Iterable

from kb_utils import ROOT, parse_frontmatter, parse_sections, write_text_if_changed


DASHBOARDS_DIR = ROOT / "dashboards"
GENERATED_START = "<!-- GENERATED:START -->"
GENERATED_END = "<!-- GENERATED:END -->"

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)(?:#[^)]+)?\)")
PRIORITY_LINE_RE = re.compile(
    r"^- `([^`]+)` from \[([^\]]+)\]\(([^)]+\.md)\)\.", re.MULTILINE
)
FRONTMATTER_REFERENCE_KEYS = {
    "related_concepts",
    "concepts",
    "variables",
    "systems",
    "questions",
    "meta_questions",
    "theories",
    "experiments",
    "related_variables",
    "related_systems",
    "related_questions",
    "related_theories",
    "related_experiments",
}


@dataclass
class Page:
    path: Path
    rel_path: str
    stem: str
    title: str
    frontmatter: dict
    sections: dict[str, str]
    body: str
    category: str
    tags: list[str]
    links: set[str] = field(default_factory=set)
    backlinks: set[str] = field(default_factory=set)
    explicit_domains: set[str] = field(default_factory=set)

    @property
    def is_cluster_theory(self) -> bool:
        return self.category == "theory" and "cluster" in self.tags

    @property
    def is_global_theory(self) -> bool:
        return self.category == "theory" and "cluster" not in self.tags

    @property
    def is_priority_doc(self) -> bool:
        return self.category == "experiment" and self.path.name == "prioritization.md"


def normalize_ref(value: str) -> str:
    text = value.strip().replace(".md", "")
    text = text.replace("_", "-").replace(" ", "-")
    text = re.sub(r"-+", "-", text)
    return text.lower().strip("-")


def rel_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def category_for_path(path: Path) -> str:
    relative = rel_path(path)
    name = path.name
    if relative.startswith("concepts/") and name != "README.md":
        return "concept"
    if relative.startswith("variables/") and name != "README.md":
        return "variable"
    if relative.startswith("systems/") and name != "README.md":
        return "system"
    if relative.startswith("experiments/") and name != "README.md":
        return "experiment"
    if relative.startswith("questions/"):
        return "question"
    if relative.startswith("meta_questions/") or "meta" in name.lower():
        return "meta-question"
    if relative.startswith("theory/cluster/") or relative.startswith("theory/global/"):
        return "theory"
    if relative.startswith("notes/"):
        return "paper"
    if relative.startswith("indexes/") or name == "README.md":
        return "index"
    return "other"


def extract_explicit_domains(frontmatter: dict, tags: list[str]) -> set[str]:
    values: list[str] = []
    for key in ("domain", "domains", "cluster", "clusters"):
        raw = frontmatter.get(key)
        if isinstance(raw, list):
            values.extend(str(item) for item in raw)
        elif raw:
            values.append(str(raw))
    values.extend(tags)

    domains: set[str] = set()
    for value in values:
        lowered = value.strip().lower()
        if "membrane" in lowered:
            domains.add("membrane")
        if "chromatin" in lowered or "genome" in lowered or "chromosome" in lowered:
            domains.add("chromatin")
    return domains


def parse_page(path: Path) -> Page:
    raw_text = path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(raw_text)
    title, sections = parse_sections(body)
    tags_raw = frontmatter.get("tags", [])
    tags = [str(tag).strip() for tag in tags_raw] if isinstance(tags_raw, list) else []
    page = Page(
        path=path,
        rel_path=rel_path(path),
        stem=path.stem,
        title=title or path.stem.replace("-", " ").replace("_", " ").title(),
        frontmatter=frontmatter,
        sections=sections,
        body=body,
        category=category_for_path(path),
        tags=tags,
    )
    page.explicit_domains = extract_explicit_domains(frontmatter, tags)
    return page


def load_pages() -> dict[str, Page]:
    pages: dict[str, Page] = {}
    for path in sorted(ROOT.rglob("*.md")):
        relative = rel_path(path)
        if relative.startswith(".venv/"):
            continue
        pages[relative] = parse_page(path)
    return pages


def build_lookup_maps(pages: dict[str, Page]) -> tuple[dict[str, Page], dict[str, Page]]:
    by_rel = {page.rel_path: page for page in pages.values()}
    by_ref: dict[str, Page] = {}
    for page in pages.values():
        for ref in {
            normalize_ref(page.stem),
            normalize_ref(page.title),
            normalize_ref(page.rel_path),
        }:
            by_ref.setdefault(ref, page)
    return by_rel, by_ref


def ensure_str_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def populate_links(pages: dict[str, Page]) -> None:
    by_rel, by_ref = build_lookup_maps(pages)
    for page in pages.values():
        links: set[str] = set()

        for match in WIKILINK_RE.findall(page.body):
            target = match.split("|", 1)[0].split("#", 1)[0].strip()
            resolved = by_ref.get(normalize_ref(target))
            if resolved is not None:
                links.add(resolved.rel_path)

        for target in MARKDOWN_LINK_RE.findall(page.body):
            resolved = resolve_markdown_link(page, target, by_rel)
            if resolved is not None:
                links.add(resolved.rel_path)

        for key in FRONTMATTER_REFERENCE_KEYS:
            for value in ensure_str_list(page.frontmatter.get(key)):
                resolved = by_ref.get(normalize_ref(value))
                if resolved is not None:
                    links.add(resolved.rel_path)

        page.links = links

    for page in pages.values():
        page.backlinks.clear()
    for page in pages.values():
        for target in page.links:
            if target in pages:
                pages[target].backlinks.add(page.rel_path)


def sort_pages(pages: Iterable[Page]) -> list[Page]:
    return sorted(pages, key=lambda page: (page.title.lower(), page.rel_path))


def page_wikilink(page: Page, alias: str | None = None) -> str:
    target = page.stem
    if alias and alias != page.stem:
        return f"[[{target}|{alias}]]"
    return f"[[{target}]]"


def heading_wikilink(page: Page, heading: str) -> str:
    return f"[[{page.stem}#{heading}|{heading}]]"


def extract_priority_items(priority_page: Page, experiment_pages: dict[str, Page]) -> list[tuple[str, Page]]:
    items: list[tuple[str, Page]] = []
    for title, _, link_target in PRIORITY_LINE_RE.findall(priority_page.body):
        resolved = resolve_markdown_link(priority_page, link_target, experiment_pages)
        if resolved is not None:
            items.append((title, resolved))
    return items


def resolve_markdown_link(
    source: Page, target: str, pages_by_rel: dict[str, Page]
) -> Page | None:
    source_dir = source.path.parent
    absolute = (source_dir / target).resolve()
    try:
        relative = absolute.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return None
    return pages_by_rel.get(relative)


def cluster_key_for_theory(page: Page) -> str | None:
    lowered = f"{page.stem} {page.title}".lower()
    if "chromatin" in lowered:
        return "chromatin"
    if "membrane" in lowered:
        return "membrane"
    return None


def has_explicit_domain(page: Page, cluster_key: str) -> bool:
    return cluster_key in page.explicit_domains


def is_adjacent_to(page: Page, target_paths: set[str]) -> bool:
    return bool((page.links | page.backlinks) & target_paths)


def matches_cluster_language(page: Page, cluster_key: str) -> bool:
    definition = page.sections.get("Definition", "")
    lowered = f"{page.stem} {page.title} {definition}".lower()
    if cluster_key == "chromatin":
        return any(term in lowered for term in ("chromatin", "genome", "genomic", "chromosome", "tad", "ctcf", "cohesin"))
    if cluster_key == "membrane":
        return any(term in lowered for term in ("membrane", "lamellar", "lipid", "cholesterol", "intermembrane", "hydration", "bilayer"))
    return False


def dedupe_pages(items: Iterable[Page]) -> list[Page]:
    return list({page.rel_path: page for page in items}.values())


def select_by_cluster(
    cluster_key: str,
    category: str,
    pages: dict[str, Page],
    seed_paths: set[str],
) -> tuple[list[Page], list[Page], list[Page]]:
    selected: list[Page] = []
    explicit: list[Page] = []
    fallback: list[Page] = []

    for page in pages.values():
        if page.category != category:
            continue
        if has_explicit_domain(page, cluster_key):
            selected.append(page)
            explicit.append(page)
            continue
        if seed_paths and is_adjacent_to(page, seed_paths):
            selected.append(page)
            fallback.append(page)

    selected = sort_pages(dedupe_pages(selected))
    explicit = sort_pages(dedupe_pages(explicit))
    fallback = [page for page in sort_pages(dedupe_pages(fallback)) if page.rel_path in {item.rel_path for item in selected}]
    return selected, explicit, fallback


def select_related_global_theories(cluster_theory: Page, global_theories: list[Page]) -> list[Page]:
    selected: list[Page] = []
    lowered = cluster_theory.body.lower()
    for theory in global_theories:
        if theory.title.lower() in lowered or theory.stem.lower() in lowered:
            selected.append(theory)
    return selected or global_theories


def select_cluster_pages(
    cluster_key: str,
    pages: dict[str, Page],
) -> tuple[dict[str, list[Page]], list[str], dict[str, list[Page]]]:
    cluster_theory = next(
        page
        for page in pages.values()
        if page.is_cluster_theory and cluster_key_for_theory(page) == cluster_key
    )
    global_theories = sort_pages(page for page in pages.values() if page.is_global_theory)
    related_theories = [cluster_theory, *select_related_global_theories(cluster_theory, global_theories)]
    cluster_seed_paths = {cluster_theory.rel_path}

    systems, explicit_systems, fallback_systems = select_by_cluster(
        cluster_key=cluster_key,
        category="system",
        pages=pages,
        seed_paths=cluster_seed_paths,
    )
    system_paths = {page.rel_path for page in systems}

    questions, explicit_questions, fallback_questions = select_by_cluster(
        cluster_key=cluster_key,
        category="question",
        pages=pages,
        seed_paths=cluster_seed_paths | system_paths,
    )
    question_paths = {page.rel_path for page in questions}

    experiments, explicit_experiments, fallback_experiments = select_by_cluster(
        cluster_key=cluster_key,
        category="experiment",
        pages=pages,
        seed_paths=cluster_seed_paths | system_paths | question_paths,
    )
    experiments = [page for page in experiments if not page.is_priority_doc]
    explicit_experiments = [page for page in explicit_experiments if not page.is_priority_doc]
    fallback_experiments = [page for page in fallback_experiments if not page.is_priority_doc]
    experiment_paths = {page.rel_path for page in experiments}

    concepts, explicit_concepts, fallback_concepts = select_by_cluster(
        cluster_key=cluster_key,
        category="concept",
        pages=pages,
        seed_paths=cluster_seed_paths | system_paths | question_paths | experiment_paths,
    )
    concept_paths = {page.rel_path for page in concepts}

    variables, explicit_variables, fallback_variables = select_by_cluster(
        cluster_key=cluster_key,
        category="variable",
        pages=pages,
        seed_paths=cluster_seed_paths | system_paths | question_paths | experiment_paths,
    )
    concept_linked_variables = sort_pages(
        pages[link]
        for concept in concepts
        for link in concept.links
        if pages[link].category == "variable" and matches_cluster_language(pages[link], cluster_key)
    )
    variables = sort_pages(dedupe_pages([*variables, *concept_linked_variables]))
    explicit_variables = sort_pages(dedupe_pages(explicit_variables))
    fallback_variables = sort_pages(
        dedupe_pages([*fallback_variables, *concept_linked_variables])
    )

    meta_questions, explicit_meta_questions, fallback_meta_questions = select_by_cluster(
        cluster_key=cluster_key,
        category="meta-question",
        pages=pages,
        seed_paths=cluster_seed_paths | question_paths,
    )

    insufficiency: list[str] = []
    fallback_counts = {
        "concepts": len(fallback_concepts),
        "variables": len(fallback_variables),
        "systems": len(fallback_systems),
        "questions": len(fallback_questions),
        "experiments": len(fallback_experiments),
        "theories": len([page for page in related_theories if not has_explicit_domain(page, cluster_key)]),
        "meta-questions": len(fallback_meta_questions),
    }
    fallback_counts = {key: value for key, value in fallback_counts.items() if value}
    if fallback_counts:
        insufficiency.append(
            f"{cluster_key}: explicit domain metadata is sparse; fallback graph membership was used for "
            + ", ".join(f"{label}={count}" for label, count in fallback_counts.items())
        )
    if not any(
        has_explicit_domain(page, cluster_key)
        for page in [*systems, *questions, *experiments, *concepts, *variables]
    ):
        insufficiency.append(
            f"{cluster_key}: selected pages currently have no explicit `{cluster_key}` domain metadata; "
            "assignment depends entirely on existing theory/system/question connectivity"
        )

    return (
        {
            "concepts": concepts,
            "variables": variables,
            "systems": systems,
            "questions": questions,
            "experiments": experiments,
            "theories": list({page.rel_path: page for page in related_theories}.values()),
            "meta_questions": meta_questions,
        },
        insufficiency,
        {
            "concepts": explicit_concepts,
            "variables": explicit_variables,
            "systems": explicit_systems,
            "questions": explicit_questions,
            "experiments": explicit_experiments,
            "meta_questions": explicit_meta_questions,
            "theories": sort_pages(page for page in related_theories if has_explicit_domain(page, cluster_key)),
        },
    )


def collect_top_experiments(
    experiment_pages: list[Page],
    priority_page: Page | None,
) -> list[str]:
    experiment_by_rel = {page.rel_path: page for page in experiment_pages}
    if priority_page is not None:
        ranked: list[str] = []
        for title, experiment_page in extract_priority_items(priority_page, experiment_by_rel):
            if experiment_page in experiment_pages:
                ranked.append(heading_wikilink(experiment_page, title))
        if ranked:
            return list(dict.fromkeys(ranked))[:5]

    fallback: list[str] = []
    for page in experiment_pages:
        headings = [
            line[2:].strip()
            for line in page.body.splitlines()
            if line.startswith("# ") and line[2:].strip() != page.title
        ]
        fallback.extend(heading_wikilink(page, heading) for heading in headings[:3])
    return fallback[:5]


def collect_bottlenecks(
    theories: list[Page],
    questions: list[Page],
    meta_questions: list[Page],
) -> list[str]:
    items: list[str] = []
    for page in meta_questions:
        items.append(f"- Meta-question: {page_wikilink(page)}")

    for theory in theories:
        for line in theory.sections.get("Open Problems", "").splitlines():
            if line.startswith("- "):
                items.append(line)
            if len(items) >= 8:
                return items[:8]

    for question in questions:
        for line in question.sections.get("Missing Evidence", "").splitlines():
            if line.startswith("- "):
                items.append(line)
                break
        if len(items) >= 8:
            break
    return items[:8]


def render_link_list(pages: list[Page]) -> str:
    if not pages:
        return "- None identified\n"
    return "\n".join(f"- {page_wikilink(page)}" for page in pages) + "\n"


def render_dashboard(
    title: str,
    description: str,
    metadata_note: str | None,
    concepts: list[Page],
    variables: list[Page],
    systems: list[Page],
    questions: list[Page],
    top_experiments: list[str],
    theories: list[Page],
    bottlenecks: list[str],
    quick_navigation_groups: list[tuple[str, list[str]]],
) -> str:
    lines = [
        f"## {title}",
        "",
        description,
        "",
    ]
    if metadata_note:
        lines.extend([f"> {metadata_note}", ""])

    lines.extend(
        [
            "### Core Concepts",
            render_link_list(concepts).rstrip(),
            "",
            "### Core Variables",
            render_link_list(variables).rstrip(),
            "",
            "### Systems",
            render_link_list(systems).rstrip(),
            "",
            "### Key Questions",
            render_link_list(questions).rstrip(),
            "",
            "### Top Experiments",
            ("\n".join(f"- {item}" for item in top_experiments) if top_experiments else "- None identified"),
            "",
            "### Related Theories",
            render_link_list(theories).rstrip(),
            "",
            "### Current Bottlenecks",
            ("\n".join(bottlenecks) if bottlenecks else "- No explicit bottlenecks extracted."),
            "",
            "### Quick Navigation",
        ]
    )

    for label, items in quick_navigation_groups:
        if not items:
            continue
        lines.append(f"- {label}: " + ", ".join(items))

    return "\n".join(lines).rstrip() + "\n"


def upsert_generated_section(path: Path, title: str, generated_body: str) -> None:
    scaffold = "\n".join(
        [
            f"# {title}",
            "",
            "> Generated by `scripts/build_dashboards.py`. Edit outside the generated block if needed.",
            "",
            GENERATED_START,
            generated_body.rstrip(),
            GENERATED_END,
            "",
        ]
    )

    if not path.exists():
        write_text_if_changed(path, scaffold)
        return

    existing = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"{re.escape(GENERATED_START)}.*?{re.escape(GENERATED_END)}", re.DOTALL
    )
    replacement = f"{GENERATED_START}\n{generated_body.rstrip()}\n{GENERATED_END}"
    if pattern.search(existing):
        updated = pattern.sub(replacement, existing, count=1)
    else:
        updated = scaffold
    write_text_if_changed(path, updated)


def build_global_dashboard(
    pages: dict[str, Page],
    priority_page: Page | None,
) -> tuple[str, dict[str, list[Page]], list[str], dict[str, list[Page]]]:
    concepts = sort_pages(page for page in pages.values() if page.category == "concept")
    variables = sort_pages(page for page in pages.values() if page.category == "variable")
    systems = sort_pages(page for page in pages.values() if page.category == "system")
    questions = sort_pages(page for page in pages.values() if page.category == "question")
    theories = sort_pages(page for page in pages.values() if page.category == "theory")
    experiments = sort_pages(
        page
        for page in pages.values()
        if page.category == "experiment" and not page.is_priority_doc
    )
    meta_questions = sort_pages(page for page in pages.values() if page.category == "meta-question")

    insufficiency: list[str] = []
    missing_domain = [
        page.rel_path
        for page in [*concepts, *variables, *systems, *questions, *theories, *experiments]
        if not page.explicit_domains
    ]
    if missing_domain:
        insufficiency.append(
            (
                f"global: explicit domain metadata is sparse for {len(missing_domain)} "
                f"selected non-note pages; the dashboard aggregates the full KB layer"
            )
        )

    metadata_note = None
    if missing_domain:
        metadata_note = (
            "Explicit cluster/domain metadata is mostly absent in concept, variable, system, "
            "theory, question, and experiment pages. Recommendation: add a normalized "
            "`domain` frontmatter field or dedicated `chromatin` / `membrane` tags where "
            "cluster assignment should be machine-readable."
        )

    body = render_dashboard(
        title="Global Dashboard",
        description="Cross-cluster summary generated from the KB graph and frontmatter metadata.",
        metadata_note=metadata_note,
        concepts=concepts,
        variables=variables,
        systems=systems,
        questions=questions,
        top_experiments=collect_top_experiments(experiments, priority_page),
        theories=theories,
        bottlenecks=collect_bottlenecks(theories, questions, meta_questions),
        quick_navigation_groups=[
            ("Dashboards", ["[[chromatin]]", "[[membrane]]", "[[global]]"]),
            ("Systems", [page_wikilink(page) for page in systems]),
            ("Questions", [page_wikilink(page) for page in questions]),
            ("Theories", [page_wikilink(page) for page in theories]),
        ],
    )
    upsert_generated_section(DASHBOARDS_DIR / "global.md", "Global Dashboard", body)
    return (
        "global",
        {
            "concepts": concepts,
            "variables": variables,
            "systems": systems,
            "questions": questions,
            "experiments": experiments,
            "theories": theories,
        },
        insufficiency,
        {
            "concepts": [],
            "variables": [],
            "systems": [],
            "questions": [],
            "experiments": [],
            "theories": [],
            "meta_questions": [],
        },
    )


def build_cluster_dashboard(
    cluster_key: str,
    title: str,
    description: str,
    pages: dict[str, Page],
    priority_page: Page | None,
) -> tuple[str, dict[str, list[Page]], list[str], dict[str, list[Page]]]:
    selected, insufficiency, explicit_membership = select_cluster_pages(cluster_key, pages)

    metadata_note = None
    if insufficiency:
        metadata_note = (
            "Explicit domain metadata is sparse in the selected non-note pages, so this "
            "dashboard prefers metadata when present and otherwise falls back to cluster theory, "
            "system, question, and experiment connectivity. Recommendation: add a lightweight "
            "`domain` field or `chromatin` / `membrane` tags to these pages for more direct assignment."
        )

    body = render_dashboard(
        title=title,
        description=description,
        metadata_note=metadata_note,
        concepts=selected["concepts"],
        variables=selected["variables"],
        systems=selected["systems"],
        questions=selected["questions"],
        top_experiments=collect_top_experiments(selected["experiments"], priority_page),
        theories=selected["theories"],
        bottlenecks=collect_bottlenecks(
            selected["theories"][:1], selected["questions"], selected["meta_questions"]
        ),
        quick_navigation_groups=[
            ("Dashboards", ["[[chromatin]]", "[[membrane]]", "[[global]]"]),
            ("Core Concepts", [page_wikilink(page) for page in selected["concepts"]]),
            ("Core Variables", [page_wikilink(page) for page in selected["variables"]]),
            ("Systems", [page_wikilink(page) for page in selected["systems"]]),
            ("Questions", [page_wikilink(page) for page in selected["questions"]]),
            ("Theories", [page_wikilink(page) for page in selected["theories"]]),
        ],
    )
    upsert_generated_section(DASHBOARDS_DIR / f"{cluster_key}.md", title, body)
    included = {
        key: selected[key]
        for key in ("concepts", "variables", "systems", "questions", "experiments", "theories")
    }
    return cluster_key, included, insufficiency, explicit_membership


def print_summary(results: list[tuple[str, dict[str, list[Page]], list[str], dict[str, list[Page]]]]) -> None:
    print("Created dashboards:")
    for name, included, insufficiency, explicit_membership in results:
        print(f"- dashboards/{name}.md")
        print("  included files:")
        included_files = {
            page.rel_path
            for key in ("concepts", "variables", "systems", "questions", "experiments", "theories")
            for page in included[key]
        }
        for rel in sorted(included_files):
            print(f"  - {rel}")
        if name != "global":
            explicit_files = {
                page.rel_path
                for key in ("concepts", "variables", "systems", "questions", "experiments", "theories")
                for page in explicit_membership.get(key, [])
            }
            print(f"  explicit-domain matches: {len(explicit_files)}")
        if insufficiency:
            print("  metadata insufficient:")
            for line in insufficiency:
                print(f"  - {line}")


def main() -> None:
    DASHBOARDS_DIR.mkdir(parents=True, exist_ok=True)

    pages = load_pages()
    populate_links(pages)

    priority_page = next(
        (page for page in pages.values() if page.is_priority_doc),
        None,
    )

    results = [
        build_cluster_dashboard(
            cluster_key="chromatin",
            title="Chromatin Dashboard",
            description="Cluster dashboard generated from chromatin theory, systems, questions, and experiments.",
            pages=pages,
            priority_page=priority_page,
        ),
        build_cluster_dashboard(
            cluster_key="membrane",
            title="Membrane Dashboard",
            description="Cluster dashboard generated from membrane theory, systems, questions, and experiments.",
            pages=pages,
            priority_page=priority_page,
        ),
        build_global_dashboard(pages, priority_page),
    ]

    print_summary(results)


if __name__ == "__main__":
    main()
