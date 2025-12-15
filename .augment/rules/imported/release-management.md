---
type: "manual"
description: "Example description"
---
# Release Management for Horus VFX Review Application

## Overview

This document describes the complete release management process for the Horus VFX Review Application, including version control, release preparation, distribution, and post-release procedures.

## Release Types

### 1. Major Release (X.0.0)
- **Purpose**: Significant new features, major architectural changes, breaking changes
- **Frequency**: Every 6-12 months
- **Branch**: `release/vX.0.0` from `develop`
- **Testing**: Full regression testing, extended QA cycle
- **Approval**: Requires stakeholder sign-off

### 2. Minor Release (X.Y.0)
- **Purpose**: New features, enhancements, non-breaking changes
- **Frequency**: Every 2-4 weeks
- **Branch**: `release/vX.Y.0` from `develop`
- **Testing**: Feature testing, regression testing
- **Approval**: Technical lead approval

### 3. Patch Release (X.Y.Z)
- **Purpose**: Bug fixes, security patches, minor improvements
- **Frequency**: As needed
- **Branch**: `release/vX.Y.Z` from `develop`
- **Testing**: Focused testing on fixed issues
- **Approval**: Development team approval

### 4. Hotfix Release (X.Y.Z)
- **Purpose**: Critical production fixes
- **Frequency**: Emergency only
- **Branch**: `hotfix/vX.Y.Z` from `main`
- **Testing**: Minimal, focused testing
- **Approval**: Emergency approval process

## Release Process

### Phase 1: Release Preparation

#### 1.1 Create Release Branch
```bash
# For regular releases
python scripts/git_branch_manager.py create-release 1.2.0

# For hotfixes
python scripts/git_branch_manager.py create-hotfix 1.2.1 "critical crash fix"
```

#### 1.2 Version Management
```bash
# Check current version
python horus_version.py --info

# Bump version (automatic in release branch creation)
python scripts/version_bump.py --bump minor --clear-prerelease
```

#### 1.3 Generate Release Notes
```bash
# Generate changelog
python scripts/release_manager.py changelog 1.2.0
```

#### 1.4 Update Documentation
- Update user documentation
- Update API documentation
- Update installation instructions
- Review and update README.md

### Phase 2: Testing and Validation

#### 2.1 Automated Testing
- Unit tests execution
- Integration tests
- Performance regression tests
- Security vulnerability scans

#### 2.2 Manual Testing
- Feature testing on target platforms
- User acceptance testing
- Compatibility testing with Open RV versions
- VFX pipeline integration testing

#### 2.3 Build Validation
```bash
# Build and test executable
python scripts/build_with_version.py --clean
```

### Phase 3: Release Finalization

#### 3.1 Merge to Main
```bash
# Finalize release
python scripts/release_manager.py finalize 1.2.0
```

#### 3.2 Create Distribution Packages
```bash
# Create distribution packages
python scripts/build_with_version.py --release
```

#### 3.3 Tag and Push
- Git tag creation: `v1.2.0`
- Push to remote repository
- Trigger automated release workflow

### Phase 4: Distribution

#### 4.1 GitHub Release
- Automated creation via GitHub Actions
- Release notes from changelog
- Attached distribution packages
- Binary executable files

#### 4.2 Internal Distribution
- Copy to internal file servers
- Update package repositories
- Notify VFX teams

#### 4.3 Documentation Updates
- Update online documentation
- Publish release notes
- Update download links

### Phase 5: Post-Release

#### 5.1 Monitoring
- Monitor for critical issues
- Track user feedback
- Performance monitoring

#### 5.2 Support
- Respond to user issues
- Prepare hotfixes if needed
- Update FAQ and troubleshooting guides

## Automated Release Workflow

### GitHub Actions Integration

The release process is automated through GitHub Actions:

1. **Trigger**: Push to tag `v*` or manual workflow dispatch
2. **Validation**: Version format, branch status, tests
3. **Build**: Cross-platform executable creation
4. **Package**: Distribution package creation
5. **Release**: GitHub release with artifacts
6. **Notify**: Team notifications

### Manual Release Commands

```bash
# Prepare release
python scripts/release_manager.py prepare 1.2.0

# Test release branch
python scripts/build_with_version.py --bump-build

# Finalize release
python scripts/release_manager.py finalize 1.2.0

# Create hotfix
python scripts/release_manager.py hotfix 1.2.1 "critical fix description"
```

## Version Numbering Strategy

### Semantic Versioning (SemVer)

**Format**: `MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]`

#### Version Components
- **MAJOR**: Incompatible API changes, major features
- **MINOR**: Backward-compatible functionality additions
- **PATCH**: Backward-compatible bug fixes
- **PRERELEASE**: alpha, beta, rc (release candidate)
- **BUILD**: Build metadata (date, git hash)

#### Examples
```
1.0.0           # Stable release
1.1.0-alpha.1   # Alpha pre-release
1.1.0-beta.2    # Beta pre-release
1.1.0-rc.1      # Release candidate
1.1.0+20240822.abc123  # With build metadata
```

### Version Lifecycle

1. **Development**: `0.1.0-dev.N+build`
2. **Alpha**: `1.0.0-alpha.N` (internal testing)
3. **Beta**: `1.0.0-beta.N` (external testing)
4. **Release Candidate**: `1.0.0-rc.N` (final testing)
5. **Stable**: `1.0.0` (production release)
6. **Patch**: `1.0.1` (bug fixes)

## Release Artifacts

### Distribution Packages

#### Windows Package
- **File**: `horus-1.2.0-windows.zip`
- **Contents**:
  - `horus-rv.exe` (main executable)
  - `version.json` (version information)
  - `build_info.json` (build metadata)
  - `sample_db/` (sample database files)
  - `README.md` (installation instructions)

#### Cross-Platform Package
- **File**: `horus-1.2.0-source.zip`
- **Contents**:
  - Complete source code
  - Build scripts
  - Documentation
  - Configuration files

### Metadata Files

#### version.json
```json
{
  "major": 1,
  "minor": 2,
  "patch": 0,
  "prerelease": null,
  "build_number": 15,
  "version_scheme": "semantic"
}
```

#### build_info.json
```json
{
  "build_timestamp": "2024-08-22T15:30:45.123456",
  "version": "1.2.0",
  "version_with_build": "1.2.0+20240822.abc123",
  "git_hash": "abc123def456",
  "git_branch": "release/v1.2.0",
  "build_machine": "GITHUB-ACTIONS",
  "python_version": "3.8.10",
  "platform": "win32"
}
```

## Quality Gates

### Pre-Release Checklist

- [ ] All tests passing
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Version number updated
- [ ] Changelog generated
- [ ] Security scan passed
- [ ] Performance benchmarks met
- [ ] Compatibility testing completed

### Release Approval Matrix

| Release Type | Approvers Required | Testing Level |
|--------------|-------------------|---------------|
| Major        | Product Owner + Tech Lead | Full |
| Minor        | Tech Lead | Standard |
| Patch        | Senior Developer | Focused |
| Hotfix       | On-call Engineer | Minimal |

## Rollback Procedures

### Emergency Rollback

1. **Immediate**: Remove download links
2. **Communication**: Notify users and teams
3. **Investigation**: Identify root cause
4. **Fix**: Prepare hotfix or revert
5. **Re-release**: Follow hotfix process

### Rollback Commands

```bash
# Revert to previous version
git checkout main
git revert <release-commit-hash>
git tag -d v1.2.0
git push origin :refs/tags/v1.2.0

# Create rollback release
python scripts/release_manager.py hotfix 1.1.1 "rollback from 1.2.0"
```

## Monitoring and Metrics

### Release Metrics
- Release frequency
- Time from development to production
- Number of hotfixes per release
- User adoption rate
- Critical issues per release

### Success Criteria
- Zero critical issues in first 48 hours
- 95% successful installations
- Positive user feedback
- Performance within acceptable limits

This release management process ensures consistent, reliable, and traceable releases of the Horus VFX Review Application while maintaining high quality standards and minimizing risk to production environments.
