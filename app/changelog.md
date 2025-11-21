# Changelog

## v1.2.0 — 2025-10-13
**Release Title:** Security Annotated Edition  
**Author:** @reggiemoorejr  

### Overview
This release introduces standardized inline documentation and embedded security best practices across core SEA-SEQ execution files.

### Changes
- Added detailed inline comments explaining workflow logic, purpose, and developer context.
- Embedded `--- Security Note ---` guidance blocks for secure coding and operations.
- Implemented standardized headers with:
  - Version: SEA-SEQ v1.2.0 — Security Annotated Edition  
  - Author: @reggiemoorejr  
  - Last Updated: October 2025  
- Applied consistent sectioning conventions (`### SECTION:` and `### STEP:`).
- Enhanced transparency and onboarding for new developers.

### Files Annotated
- `pentest_runner.py`
- `gettoken.go`
- `genid.go`
- `Dockerfile`
- `reset-sea-seq.sh`
- `destroydata.sh`
- `cleanupscript.sh`
- `shutdown.sh`

### Notes
> This update improves maintainability, onboarding speed, and operational safety across environments (local, CI/CD, and Docker).

---

## v1.0.0 — 2025-08-19
- Initial public release: runner, strict OAS checks, coverage, diff, HTML/JSON/JUnit, parallel, fail-fast, tags.
