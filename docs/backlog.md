# Ansible Dev Spaces Backlog

This backlog tracks work that belongs in the Dev Space wrapper, workspace
provisioning, manifest orchestration, and repository integration layer.

## Scope

- Dev Space startup behavior and bootstrap flow
- Manifest discovery, composition, and convenience commands
- Default working-directory and output-directory behavior
- Cross-repo document validation runs against real content repositories

## Proposed Backlog

### Near Term

1. Add a single-input `docx-render-one` workflow driven only by manifest `id`.
   The user experience should be one obvious command for rendering a single
   document from the manifest without needing to pass file paths.
2. Add manifest composition support.
   This should support child manifests and make it possible to either:
   - point at an explicit manifest path, or
   - place a manifest plus shared `logo` and `org` data in a repo root and let
     the tooling discover it automatically.
3. Provision an unversioned working folder by default.
   The output location should:
   - live outside the versioned source tree,
   - mirror the source repository name and output path structure, and
   - be designed for the most persistent storage Dev Spaces can provide.
4. Simplify manifest entries.
   The default behavior should assume output filenames match the input filename
   with the correct extension. A nullable override field should allow a
   different output name when the default would be wrong.
5. Do a cleanup pass on legacy folders, bootstrap scripts, duplicate workflow
   paths, and documentation.
6. Clone and iterate through all Markdown documents in
   `architecture-docs@develop`, generate a manifest from that corpus, and use
   it to classify issues at the correct layer:
   - authoring issue,
   - preflight gap,
   - lint gap,
   - render-wrapper gap, or
   - core renderer gap.

### Strategy

7. Decide whether the current repo should continue to host documentation
   workflow features or whether those features should move to a dedicated
   documentation Dev Space while this repo returns to being automation-focused.
8. If the split happens, define the minimum integration contract between the
   automation Dev Space and the documentation Dev Space.
9. Standardize bootstrap so cloned repos appear reliably in the workspace
   without manual repair steps.

### Next

10. Add a working-folder retention policy for semi-persistent Dev Space
    storage, including cleanup rules and user-visible folder conventions.
11. Add manifest validation commands that explain missing `logo`, `org`, child
    manifest, or output-root assumptions before a render starts.
12. Add smoke-test targets that exercise:
    - sample documents,
    - manifest discovery,
    - single-document rendering, and
    - bulk rendering against a real content repo.

## Additional Recommended Items

1. Add a repo-root convention document for content repositories that want
   zero-config rendering in Dev Spaces.
2. Add editor settings and recommended extensions for diagram authoring,
   linting, and preview so authors can catch issues before render time.
3. Add a small manifest generator for imported repositories to reduce manual
   setup when evaluating a large doc corpus.
