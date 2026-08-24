# Source record

- Origin URL: https://github.com/first-fluke/oh-my-agent
- Ref: main
- Commit SHA: `7a2b46ebe670b14be628210ea45fd3ccc24ab5ee`
- Analysis timestamp: 2026-08-24T03:55:56+09:00

## Analysis boundary

- The source was inspected read-only through GitHub API/raw-file reads. No clone, issue/PR action, repository setting change, secret read, or deployment was performed.
- `main` was resolved to the SHA above before source reading. The GitHub API reported 3,863 tree entries and `truncated: false`.
- This archive focuses on the executable CLI, installation/linking, hook and state-verification paths, the harness evaluator, representative agent/skill definitions, and CI. Large generated, vendored, lock, binary, website-localisation, and repeated skill-resource trees were not read in full.

## Access limits and excluded candidates

- Not executed: the source repository's test suite, install scripts, `oma` commands, hooks, GitHub Action, or any external agent/vendor dispatch. The archive can describe code/configuration and the declared CI workflow, but cannot assert a runtime pass for this SHA.
- The current commit message contains `[skip ci]`; GitHub Actions returned no `test.yml` run with this exact SHA. See [E21] in `06-source-evidence.md`.
- Not fully opened: 33 other skill definition roots, 9 other agent definition files, generated `prompt-manifest.json`, `bun.lock`, 3,863-path bulk tree contents, website build/static assets, translations, and documentation/reference trees outside the selected operational documents. They are excluded for scale, not treated as absent.
- Not verified against npm registry, GitHub Marketplace, external vendor products, or release artifacts; badges/readme claims about those services remain out of scope.

## Evidence notation

`[E##]` refers to a fixed-SHA source link and line range in `06-source-evidence.md`. “Confirmed” means the linked source was opened; “Inference” is explicitly marked; “Unverified” means it was not observed in this analysis.
