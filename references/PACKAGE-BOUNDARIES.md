# Package Boundaries

## Include in the package

- architecture docs
- generic templates
- generic examples
- naming conventions
- promotion workflow
- maintenance workflow guidance

## Exclude from the package

- secrets
- auth tokens
- private user notes
- machine-specific runtime artifacts
- noisy historical transcripts
- provider-specific credentials

## Keep optional

- semantic search
- vector indexing
- cron automation
- platform-specific integration layers
- hosted dashboards

## Public publishing rule

If a file would be awkward to publish on GitHub, it probably does not belong in the generic package.
