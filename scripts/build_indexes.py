#!/usr/bin/env python3

from __future__ import annotations

from collections import Counter, defaultdict

from kb_utils import (
    INDEXES_DIR,
    ensure_list,
    load_concept_records,
    load_note_records,
    load_library_note_records,
    load_synthesis_note_records,
    relative_link,
    resolved_paper_type,
    slug_to_title,
    write_text_if_changed,
)

PLACEHOLDER_CONCEPTS = {"needs-manual-review"}
PLACEHOLDER_VALUES = {"needs-manual-review"}

CLUSTER_SPECS = [
    {
        "name": "Membrane Multilayer Ordering and Interlayer Coupling",
        "members": [
            "Lee_CurrApplPhys_2017.md",
            "Lee_JACS_2024.md",
            "Tayebi_NatMat_2012.md",
        ],
        "extra_methods": [],
        "extra_variables": [],
        "extra_concepts": [],
        "summary": [
            "Studies stacked or phase-separated lipid multilayers where vertical order depends on cholesterol, phase state, and intermembrane spacing.",
            "The cluster is now a three-paper membrane core unified by exact overlap in `fluorescence microscopy`, `synchrotron x-ray reflectivity`, `lamellar spacing [D]`, `lamellar-spacing`, `liquid-ordered-phase`, and `x-ray-reflectivity`.",
        ],
        "separation": "Distinct because it is the only membrane-system cluster and the only one built around lamellar structural readouts rather than nuclear imaging or chromatin organization.",
        "uncertainty": "Low. Adding `Tayebi_NatMat_2012.md` strengthened the exact-overlap core without blurring boundaries.",
    },
    {
        "name": "Nucleolar Coalescence and Interface Dynamics",
        "members": [
            "Arsenadze_2024.md",
            "Caragine_2018.md",
            "Caragine_2019.md",
        ],
        "extra_methods": [],
        "extra_variables": [],
        "extra_concepts": [],
        "summary": [
            "Studies live-cell nucleoli as coalescing condensates, with emphasis on fusion kinetics, anomalous coarsening, interface roughness, and the influence of the surrounding nucleoplasm.",
            "The cluster remains supported by exact shared metadata such as `nucleolar-coalescence`, `nucleolar volume [V]`, `relative nucleolar velocity`, `surface-fluctuations`, and `nucleolus-nucleoplasm-interface`.",
        ],
        "separation": "Distinct from the chromatin-response and fractality clusters because the primary object is the nucleolus-nucleoplasm interface rather than bulk chromatin packing.",
        "uncertainty": "Low-medium. The core is stable, but `Arsenadze_2024.md` and `Caragine_2019.md` still bridge outward through cell-cycle framing and live-cell dynamics.",
    },
    {
        "name": "Chromatin Dynamics, Rheology, and Perturbation Response",
        "members": [
            "Caragine_2022.md",
            "Chu_2024.md",
            "Eaton_2019.md",
            "Eshghi_2021.md",
            "Rey-Millet_bioRxiv_2026.md",
        ],
        "extra_methods": [],
        "extra_variables": [],
        "extra_concepts": [],
        "summary": [
            "Studies how chromatin motion, compaction, and rheology change under mechanical stress, transcriptional activity, DNA damage, differentiation, or cell-cycle progression.",
            "This remains one of the strongest clusters in the KB, driven by repeated exact overlap in `spinning-disk confocal microscopy`, `displacement correlation spectroscopy`, `chromatin displacement correlation [Cdx]`, `mean square network displacement [MSND]`, `chromatin-compaction`, and `chromatin-dynamics`.",
        ],
        "separation": "Distinct from the packing-domain and fractality clusters because its core overlap comes from live-cell motion and rheology variables rather than domain-scale structural descriptors.",
        "uncertainty": "Low-medium. `Rey-Millet_bioRxiv_2026.md` strengthens the cell-cycle dynamics edge of the cluster but also increases bridge structure toward the fractality side.",
    },
    {
        "name": "Chromatin Packing Domains and Transcriptional Coupling",
        "members": [
            "Miron_2020.md",
            "Carter_bioRxiv_2026.md",
            "Huang_2020.md",
            "Li_2019.md",
            "Li_2021.md",
            "Li_2022.md",
            "Virk_2020.md",
        ],
        "extra_methods": [],
        "extra_variables": [],
        "extra_concepts": [],
        "summary": [
            "Studies chromatin as nanoscale packing domains whose size, density, and internal scaling couple to transcriptional state or genome connectivity.",
            "The cluster is unified by repeated exact overlap in `chromatin-packing-domains`, `chromatin packing scaling [D]`, `chromstem tomography`, `partial wave spectroscopic microscopy`, and `transcription-chromatin-coupling`, and it now includes a stronger physical-domain-versus-TAD bridge through `Miron_2020.md`.",
        ],
        "separation": "Distinct from the chromatin-dynamics cluster because the repeated overlap is structural and domain-centric, and distinct from the fractality cluster because these papers emphasize domain architecture and transcriptional coupling more than general fractal readouts.",
        "uncertainty": "Low-medium. This is a newly clear core produced jointly by the expanded corpus and stronger metadata normalization.",
    },
    {
        "name": "Chromatin Fractality and Scale-Dependent Genome Structure",
        "members": [
            "Almassalha_2017.md",
            "Iashina_2021.md",
            "Lee_BiophysJ_2025.md",
            "Li_2018.md",
            "Sung_2021.md",
            "Yi_2015.md",
        ],
        "extra_methods": [],
        "extra_variables": [],
        "extra_concepts": [],
        "summary": [
            "Collects papers that quantify chromatin or chromosome organization through fractal dimensions, mass-scaling, box-counting, scattering exponents, or related scale-dependent structural readouts.",
            "The cluster is anchored most strongly by exact overlap in `chromatin-fractality` and `fractal dimension [D]`, even though the assay families are diverse across imaging, scattering, and live-cell optical readouts.",
        ],
        "separation": "Distinct from the packing-domain cluster because its shared structure is organized around generalized scaling descriptors rather than explicit packing-domain architecture, and distinct from the chromatin-dynamics cluster because it is mostly descriptive rather than rheological.",
        "uncertainty": "Medium. The core is real and much stronger than before, but several papers on the packing-domain side remain genuine neighbors rather than cleanly separate cousins.",
    },
]

WEAKLY_ATTACHED_PAPERS = [
    {
        "paper": "Bintu_Mateo_2018_Superres.md",
        "reason": "Strongly relevant to TAD-like physical domains and cohesin-independent single-cell boundaries, but currently sits between the packing-domain and genome-architecture sides rather than inheriting one existing cluster's core metadata signature.",
    },
    {
        "paper": "Chu_2017.md",
        "reason": "Shares `cell-cycle`, `cell-cycle stage`, and `surface-fluctuations` with the nucleolar and chromatin-side papers, but lacks enough exact overlap to justify a strong hard assignment under the current heuristics.",
    },
    {
        "paper": "Dileep_2015.md",
        "reason": "Adds an early-G1 time-course for TAD re-establishment and replication-timing coupling, but currently bridges cell-cycle and genome-architecture themes rather than landing inside an existing chromatin core.",
    },
    {
        "paper": "Leidescher_2022.md",
        "reason": "Adds direct transcription-driven locus reshaping through transcription loops, but is too gene-scale and transcription-specific to belong cleanly to the existing packing-domain or dynamics cores.",
    },
    {
        "paper": "Nora_2017.md",
        "reason": "Provides strong acute CTCF perturbation evidence on insulation versus compartmentalization, but currently behaves as an architectural bridge instead of a member of the packing-domain or dynamics cores.",
    },
    {
        "paper": "Ochs_2019.md",
        "reason": "Links DNA-damage response to TAD-sized local topology stabilization, bridging damage-response dynamics and genome architecture without fully matching one existing cluster signature.",
    },
    {
        "paper": "Thiecke_2020.md",
        "reason": "Adds promoter-contact rewiring and buffered transcriptional response after acute cohesin or CTCF loss, but remains an architecture-function bridge rather than a packing-domain core member.",
    },
]

BRIDGE_CANDIDATES = [
    {
        "paper": "Li_2019.md",
        "links": "Chromatin Packing Domains and Transcriptional Coupling <-> Chromatin Fractality and Scale-Dependent Genome Structure",
        "reason": "Shares `chromatin-packing-domains` with the packing-domain cluster, but also overlaps the fractality cluster through `mass-scaling analysis`, `transmission electron microscopy`, and `fractal dimension [D]`.",
    },
    {
        "paper": "Li_2022.md",
        "links": "Chromatin Packing Domains and Transcriptional Coupling <-> Chromatin Fractality and Scale-Dependent Genome Structure",
        "reason": "Is domain-centric by `chromatin-packing-domains`, `chromatin volume concentration [CVC]`, and `packing domain radius [R_f]`, but also carries strong fractality overlap through `chromatin-fractality` and mass-scaling descriptors.",
    },
    {
        "paper": "Almassalha_2017.md",
        "links": "Chromatin Packing Domains and Transcriptional Coupling <-> Chromatin Fractality and Scale-Dependent Genome Structure",
        "reason": "Does not explicitly segment packing domains, but links fractal dimension to transcription using `partial wave spectroscopic microscopy`, making it a conceptual bridge into the packing-domain/transcription literature.",
    },
    {
        "paper": "Lee_BiophysJ_2025.md",
        "links": "Chromatin Fractality and Scale-Dependent Genome Structure <-> Chromatin Dynamics, Rheology, and Perturbation Response",
        "reason": "Belongs to the fractality side by methods and descriptors, but overlaps the dynamics cluster through `chromatin-compaction`, `cell-cycle`, and live-cell nuclear imaging.",
    },
    {
        "paper": "Miron_2020.md",
        "links": "Chromatin Packing Domains and Transcriptional Coupling <-> genome-architecture / TAD literature",
        "reason": "Adds physical `~200-300 nm` chromatin domains that can overlap TADs yet persist after cohesin ablation, making it the clearest bridge between packing-domain morphology and genomic insulation papers.",
    },
    {
        "paper": "Nora_2017.md",
        "links": "Chromatin Packing Domains and Transcriptional Coupling <-> architectural insulation / compartmentalization literature",
        "reason": "Shows that acute CTCF loss disrupts loops and TAD insulation with limited transcriptional fallout, sharpening the distinction between contact architecture and other chromatin-state layers.",
    },
    {
        "paper": "Thiecke_2020.md",
        "links": "Chromatin Packing Domains and Transcriptional Coupling <-> promoter-contact architecture literature",
        "reason": "Adds acute contact rewiring with selective transcriptional consequences, strengthening the buffered architecture-to-expression bridge.",
    },
    {
        "paper": "Chu_2017.md",
        "links": "Nucleolar Coalescence and Interface Dynamics <-> Chromatin Dynamics / Fractality boundary",
        "reason": "Remains the main weakly attached paper because it ties `surface-fluctuations` and `cell-cycle` to the rest of the KB without strongly inheriting any one cluster's full metadata signature.",
    },
]

MISSING_LINKS = [
    "A live-cell study that measures packing-domain structure and DCS-style chromatin motion in the same nuclei.",
    "A paper that combines fractal or mass-scaling readouts with explicit transcriptional perturbations across the cell cycle.",
    "A study that links nucleolar dynamics directly to genome-wide packing-domain or chromatin-rheology measurements.",
    "A membrane paper that adds live coarsening dynamics or explicit intermembrane-coupling energetics, reducing the isolation of the membrane cluster.",
]

CHANGE_SINCE_PREVIOUS_MAPPING = [
    "The membrane cluster gained `Tayebi_NatMat_2012.md` and is now a stronger three-paper structural core.",
    "The chromatin-response cluster gained `Rey-Millet_bioRxiv_2026.md`, strengthening the live-cell dynamics and cell-cycle side of that region.",
    "The chromatin packing-domain cluster now also contains `Miron_2020.md`, which strengthens the physical-domain side while explicitly sharpening the distinction between physical domains and canonical TAD insulation.",
    "The previous weak cell-cycle/fractality region split in practice: a real chromatin-fractality cluster is now visible, while `Chu_2017.md` remains as a weakly attached boundary paper instead of anchoring a full core cluster.",
    "A distinct chromatin packing-domain cluster is now justified by the expanded corpus and by improved normalization of `chromatin-packing-domains`, `chromatin packing scaling [D]`, `chromstem tomography`, and `transcription-chromatin-coupling`.",
    "Several newly ingested chromatin architecture papers do not form a separate exact-overlap core but materially densify the bridge region around TAD insulation, promoter contacts, transcription-driven locus reshaping, and early-G1 structural reassembly.",
    "No previously strong clusters merged. Instead, the enlarged chromatin side became more articulated into two neighboring but distinguishable cores: packing domains and generalized fractality.",
    "Bridge candidates changed materially: `Miron_2020.md`, `Nora_2017.md`, `Thiecke_2020.md`, `Li_2019.md`, `Li_2022.md`, and `Almassalha_2017.md` now define a denser architecture-to-packing bridge region on the chromatin side.",
    "Overall uncertainty decreased because the corpus is larger and the chromatin-side overlaps are denser, but `Chu_2017.md` remains a genuine borderline paper and `Eaton_2020.md` is excluded as a duplicate record.",
]

CLUSTER_DELTA_LINES = [
    "# Cluster Deltas",
    "",
    "Generated from the refreshed frontmatter normalization and compared against the previous `indexes/clusters.md` mapping.",
    "",
    "## Paper Movements",
    "",
    "- `Tayebi_NatMat_2012.md` joined the membrane cluster.",
    "- `Rey-Millet_bioRxiv_2026.md` joined the chromatin dynamics/rheology cluster.",
    "- `Miron_2020.md`, `Carter_bioRxiv_2026.md`, `Huang_2020.md`, `Li_2019.md`, `Li_2021.md`, `Li_2022.md`, and `Virk_2020.md` now define the chromatin packing-domain cluster.",
    "- `Almassalha_2017.md`, `Iashina_2021.md`, `Lee_BiophysJ_2025.md`, `Li_2018.md`, `Sung_2021.md`, and `Yi_2015.md` now form a distinct chromatin fractality cluster.",
    "- `Bintu_Mateo_2018_Superres.md`, `Dileep_2015.md`, `Leidescher_2022.md`, `Nora_2017.md`, `Ochs_2019.md`, `Thiecke_2020.md`, and `Chu_2017.md` are recorded as weakly attached or bridge papers rather than forced into a hard exact-overlap core.",
    "- `Eaton_2020.md` is tracked as a duplicate record of `Eaton_2019.md` and excluded from derived scientific indexes.",
    "",
    "## Stronger Exact Overlaps",
    "",
    "- [Li_2019.md](../notes/Li_2019.md) <-> [Li_2022.md](../notes/Li_2022.md): share 8 exact metadata fields, making the ChromSTEM packing-domain core explicit.",
    "- [Carter_bioRxiv_2026.md](../notes/Carter_bioRxiv_2026.md) <-> [Li_2021.md](../notes/Li_2021.md): share 6 exact fields around packing domains, `chromstem tomography`, PWS, and transcription coupling.",
    "- [Caragine_2022.md](../notes/Caragine_2022.md) <-> [Chu_2024.md](../notes/Chu_2024.md): still share 7 exact metadata fields, preserving the strong chromatin-response core.",
    "- [Caragine_2022.md](../notes/Caragine_2022.md) <-> [Eshghi_2021.md](../notes/Eshghi_2021.md): still share 7 exact metadata fields, keeping the rheology branch cohesive.",
    "- [Lee_CurrApplPhys_2017.md](../notes/Lee_CurrApplPhys_2017.md) <-> [Tayebi_NatMat_2012.md](../notes/Tayebi_NatMat_2012.md): share 7 exact membrane-ordering fields, strengthening the membrane cluster.",
    "",
    "## Newly Exposed Bridge Structure",
    "",
    "- [Li_2019.md](../notes/Li_2019.md) and [Li_2022.md](../notes/Li_2022.md) visibly connect the packing-domain core to the broader fractality literature.",
    "- [Miron_2020.md](../notes/Miron_2020.md) connects physical chromatin domains to the TAD and architectural-insulation literature without collapsing those concepts.",
    "- [Nora_2017.md](../notes/Nora_2017.md) and [Thiecke_2020.md](../notes/Thiecke_2020.md) create a clearer architecture-to-transcription bridge around acute perturbation logic.",
    "- [Almassalha_2017.md](../notes/Almassalha_2017.md) bridges fractal topology papers to transcription-coupling papers through PWS and expression profiling.",
    "- [Lee_BiophysJ_2025.md](../notes/Lee_BiophysJ_2025.md) bridges fractality metrics to the live-cell chromatin-dynamics side through `chromatin-compaction` and `cell-cycle`.",
    "- [Chu_2017.md](../notes/Chu_2017.md) remains the clearest weak attachment between nucleolar/cell-cycle fluctuation work and the rest of the nucleus-side KB.",
    "",
    "## Unresolved Ambiguities",
    "",
    "- [Chu_2017.md](../notes/Chu_2017.md) is still the least stable assignment and remains intentionally weakly attached instead of forced into a strong cluster.",
    "- [Huang_2020.md](../notes/Huang_2020.md), [Li_2019.md](../notes/Li_2019.md), and [Li_2022.md](../notes/Li_2022.md) each sit close to both the packing-domain and fractality clusters.",
    "- `Bintu_Mateo_2018_Superres.md`, `Dileep_2015.md`, `Leidescher_2022.md`, `Nora_2017.md`, `Ochs_2019.md`, and `Thiecke_2020.md` increase the size of the chromatin architecture bridge region without yet creating a separate exact-overlap architecture cluster.",
    "- The membrane cluster remains isolated from the nucleus-side literature because there are still no shared variables or concepts linking lamellar spacing/order papers to chromatin papers.",
]


def note_link(index_path, record) -> str:
    return f"[{record.title}]({relative_link(index_path, record.path)})"


def note_file_link(index_path, record) -> str:
    return f"[{record.path.name}]({relative_link(index_path, record.path)})"


def concept_link(index_path, concept_slug: str, concept_record) -> str:
    if concept_record is None:
        return "-"
    concept_title = str(concept_record.frontmatter.get("title") or concept_record.title or slug_to_title(concept_slug))
    return f"[{concept_title}]({relative_link(index_path, concept_record.path)})"


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def clean_list(value) -> list[str]:
    return [
        item
        for item in ensure_list(value)
        if item not in PLACEHOLDER_VALUES
    ]


def year_sort_key(record) -> tuple[int, int, str]:
    raw_year = record.frontmatter.get("year", 0)
    try:
        year = int(raw_year or 0)
    except (TypeError, ValueError):
        year = 0
    unknown_year = 1 if year <= 0 else 0
    return (unknown_year, -year, record.title.lower())


def scientific_records(records):
    return [record for record in records]


def dominant_items(records, field: str, extras: list[str] | None = None, limit: int = 6) -> list[str]:
    counts = Counter()
    for record in records:
        counts.update(clean_list(record.frontmatter.get(field)))

    ranked = [item for item, _ in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0].lower()))]
    items: list[str] = []
    for item in ranked:
        if item not in items:
            items.append(item)
    for item in extras or []:
        if item not in items:
            items.append(item)
    return items[:limit]


def render_bullets(items: list[str], fallback: str) -> list[str]:
    if not items:
        return [f"- {fallback}"]
    return [f"- {item}" for item in items]


def build_cluster_delta_index() -> str:
    return "\n".join(CLUSTER_DELTA_LINES)


def build_cluster_index(records) -> str:
    path = INDEXES_DIR / "clusters.md"
    lookup = {record.path.name: record for record in records}
    total_notes = len(load_note_records())
    excluded_count = total_notes - len(records)
    clustered_count = sum(len(spec["members"]) for spec in CLUSTER_SPECS)
    placeholder_notes = sum(
        1
        for record in records
        if any(placeholder in ensure_list(record.frontmatter.get(field)) for field in ("methods", "variables", "concepts") for placeholder in PLACEHOLDER_VALUES)
    )

    lines = [
        "# Knowledge Base Clusters",
        "",
        "Generated from exact frontmatter overlap in `methods`, `variables`, and `concepts` after note normalization. Note-body fallback is used only for cluster naming and interpretation.",
        "Notes with `include_in_synthesis: false` are excluded from this synthesis view by default.",
        "",
        "## Overall Summary",
        f"- Total note files scanned: {total_notes}",
        f"- Scientific papers considered: {len(records)}",
        f"- Notes excluded from cluster synthesis: {excluded_count}",
        f"- Clustered papers: {clustered_count}",
        f"- Weakly attached papers: {len(WEAKLY_ATTACHED_PAPERS)}",
        f"- Cluster count: {len(CLUSTER_SPECS)}",
        f"- Notes with placeholder method/variable/concept metadata: {placeholder_notes} of {len(records)}",
        "- Core structure: 5 meaningful clusters, with the chromatin side now split into a packing-domain core and a broader fractality core.",
        "- Separation: the membrane cluster remains the most isolated component, while the packing-domain and fractality clusters are the closest neighboring pair.",
        "",
    ]

    for index, spec in enumerate(CLUSTER_SPECS, start=1):
        cluster_records = [lookup[name] for name in spec["members"] if name in lookup]
        methods = spec.get("dominant_methods") or dominant_items(cluster_records, "methods", spec["extra_methods"])
        variables = spec.get("dominant_variables") or dominant_items(cluster_records, "variables", spec["extra_variables"])
        concepts = spec.get("dominant_concepts") or dominant_items(cluster_records, "concepts", spec["extra_concepts"])

        lines.extend(
            [
                f"## {index}. {spec['name']}",
                "",
                "### Papers",
            ]
        )
        lines.extend(
            f"- {note_file_link(path, record)}"
            for record in cluster_records
        )
        lines.extend(
            [
                "",
                "### Dominant Methods",
            ]
        )
        lines.extend(render_bullets(methods, "No method overlap beyond generic microscopy."))
        lines.extend(
            [
                "",
                "### Dominant Variables",
            ]
        )
        lines.extend(render_bullets(variables, "Variables are too sparse to summarize beyond generic microscopy."))
        lines.extend(
            [
                "",
                "### Dominant Concepts",
            ]
        )
        lines.extend(render_bullets(concepts, "Concept tags remain too sparse or placeholder-heavy for a clean summary."))
        lines.extend(
            [
                "",
                "### Summary",
            ]
        )
        lines.extend(f"- {item}" for item in spec["summary"])
        lines.extend(
            [
                "",
                "### Separation",
                f"- {spec['separation']}",
                "",
                "### Uncertainty",
                f"- {spec['uncertainty']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Weakly Attached or Borderline Papers",
            "",
        ]
    )
    for item in WEAKLY_ATTACHED_PAPERS:
        record = lookup.get(item["paper"])
        paper_ref = note_file_link(path, record) if record is not None else f"`{item['paper']}`"
        lines.append(f"- {paper_ref}: {item['reason']}")
    lines.append("")

    lines.extend(
        [
            "## Change Since Previous Mapping",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in CHANGE_SINCE_PREVIOUS_MAPPING)
    lines.append("")

    lines.extend(
        [
            "## Bridge Candidates",
            "",
        ]
    )
    for item in BRIDGE_CANDIDATES:
        record = lookup.get(item["paper"])
        paper_ref = note_file_link(path, record) if record is not None else f"`{item['paper']}`"
        lines.append(f"- {paper_ref}: {item['links']}. {item['reason']}")

    lines.extend(
        [
            "",
            "## Missing Links",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in MISSING_LINKS)
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            f"- There are {len(CLUSTER_SPECS)} clusters in the current KB.",
            "- Four clusters are strong cores; one additional chromatin-fractality cluster is coherent but more bridge-rich at its perimeter.",
            "- The membrane multilayer cluster is still the most isolated component.",
            "- The chromatin packing-domain and chromatin dynamics clusters are the strongest by internal exact overlap.",
            "- Most remaining ambiguity is now concentrated in a small number of bridge or borderline papers rather than in missing normalization.",
            "- See [cluster_deltas.md](./cluster_deltas.md) for the explicit overlap changes and unresolved ambiguities.",
        ]
    )

    return "\n".join(lines)


def build_year_index(records) -> str:
    path = INDEXES_DIR / "papers_by_year.md"
    sorted_records = sorted(records, key=year_sort_key)
    rows = []
    for record in sorted_records:
        rows.append(
            [
                str(record.frontmatter.get("year", "")),
                note_link(path, record),
                str(record.frontmatter.get("journal", "")),
                resolved_paper_type(record),
                str(record.frontmatter.get("confidence", "")),
            ]
        )
    return "\n".join(
        [
            "# Papers by Year",
            "",
            "Generated from note frontmatter in `notes/`.",
            "",
            render_table(["Year", "Paper", "Journal", "Paper Type", "Confidence"], rows),
        ]
    )


def build_method_index(records) -> str:
    path = INDEXES_DIR / "papers_by_method.md"
    grouped = defaultdict(list)
    for record in records:
        for method in ensure_list(record.frontmatter.get("methods")):
            grouped[method].append(record)

    rows = []
    for method in sorted(grouped):
        linked_papers = "<br>".join(note_link(path, record) for record in sorted(grouped[method], key=lambda item: item.title.lower()))
        rows.append([method, str(len(grouped[method])), linked_papers])

    return "\n".join(
        [
            "# Papers by Method",
            "",
            "Generated from frontmatter `methods` lists.",
            "",
            render_table(["Method", "Paper Count", "Papers"], rows),
        ]
    )


def build_system_index(records) -> str:
    path = INDEXES_DIR / "papers_by_system.md"
    grouped = defaultdict(list)
    for record in records:
        system_type = str(record.frontmatter.get("system_type", "")).strip()
        grouped[system_type].append(record)

    rows = []
    for system_type in sorted(grouped):
        linked_papers = "<br>".join(note_link(path, record) for record in sorted(grouped[system_type], key=lambda item: item.title.lower()))
        rows.append([system_type, str(len(grouped[system_type])), linked_papers])

    return "\n".join(
        [
            "# Papers by System",
            "",
            "Generated from frontmatter `system_type` values.",
            "",
            render_table(["System Type", "Paper Count", "Papers"], rows),
        ]
    )


def build_concept_index(records, concept_records) -> str:
    path = INDEXES_DIR / "papers_by_concept.md"
    concept_lookup = {
        str(record.frontmatter.get("concept_id", "")).strip(): record
        for record in concept_records
    }
    grouped = defaultdict(list)
    for record in records:
        for concept in ensure_list(record.frontmatter.get("concepts")):
            if concept in PLACEHOLDER_CONCEPTS:
                continue
            grouped[concept].append(record)

    rows = []
    for concept in sorted(grouped):
        linked_papers = "<br>".join(note_link(path, record) for record in sorted(grouped[concept], key=lambda item: item.title.lower()))
        rows.append(
            [
                f"`{concept}`",
                concept_link(path, concept, concept_lookup.get(concept)),
                str(len(grouped[concept])),
                linked_papers,
            ]
        )

    return "\n".join(
        [
            "# Papers by Concept",
            "",
            "Generated from frontmatter `concepts` lists.",
            "",
            render_table(["Concept Tag", "Concept Page", "Paper Count", "Papers"], rows),
        ]
    )


def main() -> None:
    browsing_records = scientific_records(load_library_note_records())
    records = scientific_records(load_synthesis_note_records())
    concept_records = load_concept_records()
    INDEXES_DIR.mkdir(parents=True, exist_ok=True)

    write_text_if_changed(INDEXES_DIR / "papers_by_year.md", build_year_index(browsing_records))
    write_text_if_changed(INDEXES_DIR / "papers_by_method.md", build_method_index(browsing_records))
    write_text_if_changed(INDEXES_DIR / "papers_by_system.md", build_system_index(browsing_records))
    write_text_if_changed(INDEXES_DIR / "papers_by_concept.md", build_concept_index(browsing_records, concept_records))
    write_text_if_changed(INDEXES_DIR / "clusters.md", build_cluster_index(records))
    write_text_if_changed(INDEXES_DIR / "cluster_deltas.md", build_cluster_delta_index())

    print("Rebuilt indexes in indexes/")


if __name__ == "__main__":
    main()
