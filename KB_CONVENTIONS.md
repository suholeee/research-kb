# KB Conventions

This repository is a markdown-first scientific knowledge base. Files are the source of truth. Keep conventions stable so notes, synthesis pages, dashboards, indexes, and scripts operate on the same structure without hidden tooling assumptions.

## Source Hierarchy

- Prefer source PDFs over extracted text when they conflict.
- Use extracted text for speed, but verify important quantitative claims against the PDF.
- Treat `notes/` as the primary paper-level evidence layer.
- Treat `indexes/`, `dashboards/`, and `outputs/` as derived layers.
- Do not let a downstream summary overwrite an upstream grounded claim.

## Filename Conventions

- Paper notes: `notes/FirstAuthor_Journal_Year.md`
- Source PDFs: `raw/papers/FirstAuthor_Journal_Year.pdf`
- Extracted text: `raw/extracted/FirstAuthor_Journal_Year.txt`
- Concept pages: `concepts/lowercase-kebab-case.md`
- Variable pages: `variables/lowercase-kebab-case.md`
- Relationship pages: `relationships/variable-a--variable-b.md`
- System pages: `systems/lowercase-kebab-case-system.md`
- Question pages: `questions/lowercase-kebab-case.md`
- Meta-question pages: `meta_questions/lowercase-kebab-case.md`
- Theory pages: `theory/global/lowercase-kebab-case-theory.md` or `theory/cluster/lowercase-kebab-case-theory.md`
- Experiment pages: `experiments/lowercase-kebab-case-experiments.md` or similarly clear snake/kebab-case research-program names already used in the repo
- Dashboards: `dashboards/global.md`, `dashboards/chromatin.md`, `dashboards/membrane.md`
- Generated indexes: `indexes/*.md`
- Generated outputs: `outputs/*.md`, `outputs/*.json`, `outputs/*.csv`, `outputs/*.tsv`

Prefer boring, grep-friendly names over clever ones.

## Layer Responsibilities

- `notes/`: paper-level structured evidence. This is the hard-schema layer.
- `concepts/`: reusable cross-paper concept synthesis.
- `variables/`: normalization pages for recurring variables and notation conflicts.
- `relationships/`: supported interactions between variables.
- `systems/`: short multivariable pathway pages built from the relationship layer plus note wording.
- `questions/`: evidence-grounded research questions.
- `meta_questions/`: cross-cluster or cross-domain questions.
- `theory/`: grounded abstractions built from notes, concepts, systems, and questions.
- `experiments/`: decisive follow-up experiments grounded in the current theory and question structure.
- `dashboards/`: generated graph-style navigation pages.
- `indexes/`: generated metadata-driven navigation pages.
- `outputs/`: generated reports and reusable derived artifacts.

Do not duplicate a paper summary across multiple layers when a note plus links is enough.

## Required Paper Note Structure

Every paper note must contain:

1. YAML frontmatter with normalized metadata.
2. One `# Title` heading matching frontmatter `title`.
3. The following `##` sections in this stable order:
   `Citation`, `Core Question`, `System`, `Methods`, `Key Variables`, `Main Findings`, `Quantitative Results`, `Mechanism / Interpretation`, `Evidence Map`, `Limitations`, `Concepts`, `Confidence`, `Open Questions`

The validator checks both presence and order of these sections.

## Required Note Frontmatter

Required fields:

- `note_key`
- `title`
- `authors`
- `year`
- `journal`
- `doi`
- `source_pdf`
- `source_text`
- `paper_type`
- `include_in_synthesis`
- `domain`
- `system_type`
- `methods`
- `variables`
- `concepts`
- `confidence`

Also required in note tags:

- every note must include the tag `paper`
- review notes must include the tag `review`
- non-review notes must not include the tag `review`

Keep frontmatter minimal and stable. Do not add tool-specific metadata unless it is clearly reusable.

## Paper-Type Policy

Canonical `paper_type` values:

- `research_article`
- `review`
- `perspective`
- `methods_resource`
- `unknown`

Use `include_in_synthesis: true|false` explicitly. Review and perspective notes usually stay in the library but are excluded from synthesis unless there is a deliberate reason to include them.

## Concept Tag Normalization

- Use lowercase kebab-case tags such as `x-ray-reflectivity` and `chromatin-fractality`.
- Prefer reusable concepts over paper-specific phrases.
- Avoid sentence fragments, vague adjectives, and temporary placeholders unless uncertainty must be made explicit.
- Use one canonical tag per concept. Record synonyms in concept pages, not by multiplying note tags.

Examples:

- Use `x-ray-reflectivity`, not `xr`, `xray reflectivity`, or `synchrotron xr`
- Use `liquid-ordered-phase`, not `LO phase`
- Use `chromatin-packing-domains`, not a note-specific phrase such as `chromstem-domain-result`

## Method Naming

Methods in frontmatter should be normalized lower-case phrases.

Preferred examples:

- `synchrotron x-ray reflectivity`
- `fluorescence microscopy`
- `spinning-disk confocal microscopy`
- `all-atom molecular dynamics`
- `mass-scaling analysis`
- `box-counting analysis`
- `lacunarity analysis`
- `multifractal analysis`

Preserve the paper's exact wording in the note body when it matters, but keep frontmatter method names normalized.

## Variable Representation

- In note frontmatter and `## Key Variables`, use concise normalized names.
- Preserve original notation in brackets when available.
- Keep units, ranges, thresholds, and conditions in the note body, especially `## Quantitative Results`.
- Do not collapse distinct observables just because they share a symbol.

Examples:

- `lamellar spacing [D]`
- `intermembrane distance [D]`
- `hydrogen bonds per water molecule [n_HB]`
- `grayscale box-counting dimension [d_b;g]`

## Evidence And Interpretation Rules

- Separate direct findings from mechanism or interpretation.
- Do not promote cited background literature into this paper's findings.
- Preserve variables, units, ranges, thresholds, and conditions exactly when supported.
- Do not hallucinate figure interpretations.
- If extraction is weak or the PDF is needed to resolve ambiguity, mark uncertainty explicitly.
- If evidence is provisional, say so in the relevant section instead of smoothing it over.

## Conventions For Other KB Pages

Only paper notes have a strict validator-backed schema. The layers below should stay structurally regular, but they are allowed to evolve when the KB grows.

### Concept Pages

- Use `templates/concept_template.md` as the starting point.
- Keep frontmatter small and stable.
- Synthesize evidence across papers instead of restating one note.
- Typical sections: `Definition`, `How Measured`, `Evidence Across Papers`, `Quantitative Summary`, `Conflicts / Discrepancies`, `Related Concepts`, `Source Papers`

### Variable Pages

- Use one canonical variable per page.
- Normalize notation conflicts without pretending equivalent symbols always mean the same thing.
- Typical sections: `Definition`, `Units`, `Where Used`, `Measurement Methods`, `Conflicts / Ambiguities`

### Relationship Pages

- One page per supported variable pair.
- Keep the filename symmetric and stable with `--`.
- Typical sections: `Variables`, `Relationship`, `Evidence`, `Interpretation`, `Caveats`, `Confidence`

### System Pages

- Use systems to group a small number of linked variables or branches.
- Prefer short pathway structures over dense all-to-all graphs.
- Typical sections: `Variables`, `Interaction Structure`, `Evidence`, `Interpretation`, `Competing Models (if any)`, `Confidence`

### Question Pages

- Question pages are cluster-scoped research questions where one phenomenon has multiple proposed mechanisms.
- Titles should be explicit research questions, not vague topics.
- Keep the page grounded in current evidence and current unknowns.
- Typical sections: `Core Question`, `Competing Models`, `Supporting Evidence`, `Missing Evidence`, `Testable Predictions`, `Confidence`

### Meta-Question Pages

- Meta-question pages are cross-system synthesis questions that ask whether shared organizational principles span multiple systems or clusters.
- They are structurally distinct from question pages: rather than competing models for one phenomenon, meta-questions document how multiple systems compare against a candidate shared template.
- Titles should be explicit cross-system questions.
- Typical sections: `Systems Involved`, `Shared Structure`, `Differences`, `Unified Hypothesis`, `Testable Predictions`, `Confidence`
- The `Systems Involved` section should link to the cluster-level question pages that compose the meta-question.
- The `Differences` section captures where systems diverge from the shared template, not competing models for a single system.
- The `Unified Hypothesis` section states the proposed cross-system reconciliation.

### Theory Pages

- Theory pages are grounded abstractions, not literature reviews.
- They should compress recurring structure from notes, concepts, systems, and questions.
- Typical sections in the current repo include `Core Idea`, `Key Principles`, `Conceptual Structure`, `Supporting Systems`, `What It Explains`, `Predictions`, `Failure Modes`, `Open Problems`, `Confidence`

### Experiment Pages

- Experiment pages should propose decisive follow-up tests, not full project plans.
- Ground them in current questions, systems, and theory pages.
- The current pattern is a short framing section followed by named experiment blocks with `Question`, `Competing Models`, `Experimental Design`, `Expected Outcomes`, and `Feasibility`

### Dashboards, Indexes, And Outputs

- `dashboards/` is generated by `python scripts/build_dashboards.py`; preserve the generated block markers.
- `indexes/` is generated by `python scripts/build_indexes.py`.
- `outputs/` should remain reproducible and readable in git.
- Do not treat generated files as the only copy of important scientific content.

## Linking And Markdown Style

- Prefer plain markdown that stays readable in git diffs.
- Use explicit note links when citing paper support from higher layers.
- Wikilinks are used in several synthesis pages and dashboards; keep targets stable when renaming files.
- Keep frontmatter parseable and simple.

## Workflow Rules

- When notes change, run `python scripts/validate_notes.py`.
- When note metadata changes, run `python scripts/build_indexes.py`.
- When concept tags or concept pages change, run `python scripts/extract_concepts.py`.
- When higher-level synthesis pages change enough to affect navigation, run `python scripts/build_dashboards.py`.
- Use `python scripts/report_kb_stats.py` for a quick audit when normalization or coverage is in doubt.

## Infrastructure Rule

Do not introduce a database server, vector DB, or web app unless explicitly requested. Future tooling should derive from the markdown files instead of replacing them.
