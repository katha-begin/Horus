# Git Branching Strategy for Horus VFX Review Application

## Overview

This document defines the Git branching strategy for the Horus VFX Review Application, based on a modified Git Flow approach optimized for VFX software development.

## Branch Types and Naming Conventions

### Main Branches

#### `main`
- **Purpose**: Production-ready code
- **Protection**: Protected branch with required reviews
- **Merges from**: `release/*` and `hotfix/*` branches only
- **Direct commits**: Not allowed
- **Tagging**: All releases are tagged from this branch

#### `develop`
- **Purpose**: Integration branch for features
- **Protection**: Protected branch with required reviews
- **Merges from**: `feature/*`, `bugfix/*`, and `hotfix/*` branches
- **Direct commits**: Limited to minor fixes
- **Deployment**: Continuous deployment to development environment

#### `staging`
- **Purpose**: Pre-production testing and validation
- **Protection**: Protected branch
- **Merges from**: `develop` branch via pull request
- **Deployment**: Automatic deployment to staging environment
- **Testing**: Full QA testing and client review

### Supporting Branches

#### Feature Branches: `feature/*`
- **Naming**: `feature/HORUS-123-media-browser-enhancement`
- **Format**: `feature/[TICKET-ID]-[short-description]`
- **Branched from**: `develop`
- **Merged to**: `develop`
- **Lifetime**: Until feature is complete and merged
- **Examples**:
  - `feature/HORUS-001-annotation-system`
  - `feature/HORUS-002-timeline-sequencer`
  - `feature/HORUS-003-color-management`

#### Bugfix Branches: `bugfix/*`
- **Naming**: `bugfix/HORUS-456-fix-media-loading`
- **Format**: `bugfix/[TICKET-ID]-[short-description]`
- **Branched from**: `develop`
- **Merged to**: `develop`
- **Lifetime**: Until bug is fixed and merged

#### Release Branches: `release/*`
- **Naming**: `release/v1.2.0`
- **Format**: `release/v[MAJOR].[MINOR].[PATCH]`
- **Branched from**: `develop`
- **Merged to**: `main` and `develop`
- **Purpose**: Release preparation, bug fixes, version bumping
- **Lifetime**: Until release is deployed and merged

#### Hotfix Branches: `hotfix/*`
- **Naming**: `hotfix/v1.2.1-critical-crash-fix`
- **Format**: `hotfix/v[VERSION]-[short-description]`
- **Branched from**: `main`
- **Merged to**: `main` and `develop`
- **Purpose**: Critical production fixes
- **Lifetime**: Until hotfix is deployed

#### Experimental Branches: `experiment/*`
- **Naming**: `experiment/new-rendering-engine`
- **Format**: `experiment/[description]`
- **Branched from**: `develop`
- **Merged to**: `develop` (if successful) or deleted
- **Purpose**: Proof of concepts and experimental features

## Workflow Processes

### Feature Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/HORUS-123-new-feature
   ```

2. **Development**
   - Make commits with descriptive messages
   - Push regularly to remote branch
   - Keep branch up to date with develop

3. **Prepare for Merge**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout feature/HORUS-123-new-feature
   git rebase develop
   ```

4. **Create Pull Request**
   - Target: `develop` branch
   - Include: Feature description, testing notes, screenshots
   - Assign: Code reviewers
   - Link: Related tickets/issues

5. **Code Review and Merge**
   - Address review feedback
   - Squash commits if needed
   - Merge via pull request

### Release Workflow

1. **Create Release Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/v1.2.0
   ```

2. **Release Preparation**
   - Bump version numbers
   - Update changelog
   - Final testing and bug fixes
   - Update documentation

3. **Deploy to Staging**
   ```bash
   git push origin release/v1.2.0
   # Automatic deployment to staging environment
   ```

4. **QA Testing and Client Review**
   - Full regression testing
   - Client approval process
   - Bug fixes committed to release branch

5. **Merge to Main**
   ```bash
   git checkout main
   git merge --no-ff release/v1.2.0
   git tag -a v1.2.0 -m "Release version 1.2.0"
   git push origin main --tags
   ```

6. **Merge Back to Develop**
   ```bash
   git checkout develop
   git merge --no-ff release/v1.2.0
   git push origin develop
   ```

7. **Cleanup**
   ```bash
   git branch -d release/v1.2.0
   git push origin --delete release/v1.2.0
   ```

### Hotfix Workflow

1. **Create Hotfix Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/v1.2.1-critical-fix
   ```

2. **Fix and Test**
   - Implement minimal fix
   - Test thoroughly
   - Update version number

3. **Merge to Main**
   ```bash
   git checkout main
   git merge --no-ff hotfix/v1.2.1-critical-fix
   git tag -a v1.2.1 -m "Hotfix version 1.2.1"
   git push origin main --tags
   ```

4. **Merge to Develop**
   ```bash
   git checkout develop
   git merge --no-ff hotfix/v1.2.1-critical-fix
   git push origin develop
   ```

## Branch Protection Rules

### Main Branch Protection
- Require pull request reviews (minimum 2 reviewers)
- Require status checks to pass
- Require branches to be up to date before merging
- Restrict pushes to administrators only
- Require signed commits

### Develop Branch Protection
- Require pull request reviews (minimum 1 reviewer)
- Require status checks to pass
- Allow administrators to bypass requirements
- Delete head branches after merge

### Staging Branch Protection
- Require pull request reviews (minimum 1 reviewer)
- Require status checks to pass
- Automatic deployment on merge

## Commit Message Conventions

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples
```
feat(media-browser): add thumbnail caching system

Implement LRU cache for media thumbnails to improve performance
when browsing large media libraries.

- Add ThumbnailCache class with configurable size limits
- Integrate cache with MediaBrowserWidget
- Add cache statistics and monitoring

Closes HORUS-123
```

```
fix(annotation): resolve crash when deleting annotations

Fix null pointer exception when deleting the last annotation
in a frame.

Fixes HORUS-456
```

## Continuous Integration Integration

### Automated Checks
- **Code Quality**: Linting, formatting checks
- **Testing**: Unit tests, integration tests
- **Security**: Dependency vulnerability scanning
- **Performance**: Performance regression tests
- **Documentation**: Documentation build verification

### Deployment Triggers
- **Develop → Development Environment**: Automatic on merge
- **Staging → Staging Environment**: Automatic on merge
- **Main → Production Environment**: Manual approval required

## Tools and Scripts

### Branch Management Scripts
- `scripts/create_feature_branch.py`: Create feature branch with proper naming
- `scripts/create_release_branch.py`: Create release branch and bump version
- `scripts/merge_release.py`: Automated release merge workflow
- `scripts/create_hotfix.py`: Create hotfix branch from main

### Git Hooks
- **pre-commit**: Code formatting, linting
- **commit-msg**: Commit message validation
- **pre-push**: Run tests before pushing

This branching strategy ensures code quality, enables parallel development, and provides a clear path from development to production while maintaining the stability required for professional VFX software.
