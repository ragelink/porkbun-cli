# Changelog

All notable changes to the Porkbun CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2024-03-19

### Added
- Service templates for more providers:
  - AWS Route 53
  - GitHub Pages
  - Vercel
  - Shopify
  - Digital Ocean
  - Firebase
- Enhanced template customization with extended placeholder support
- Helper script (`setup_domain_services.py`) with support for all new templates
- Service-specific command-line parameters for better customization
- Comprehensive documentation for all new service templates
- AI usage disclaimer
- Porkbun appreciation statement

### Changed
- Improved template validation with placeholder skip logic
- Enhanced documentation organization and structure
- Updated GitHub Actions for better documentation builds
- Streamlined package publishing workflow

### Fixed
- Template placeholder replacement consistency
- Documentation build process
- Minor bugs in template handling

## [0.2.0] - 2024-03-16

### Added
- Service templates for domain setup (Cloudflare, Google Workspace, Office 365, Netlify)
- Template customization script (`customize_template.py`)
- Domain setup helper script (`setup_domain_services.py`)
- Batch operations with YAML configuration
- Workflow system for automated tasks
- URL forwarding commands
- Email forwarding integration
- Comprehensive documentation
- GitHub Pages integration
- PyPI publishing workflow

### Changed
- Improved error handling for API requests
- Enhanced logging and output formatting
- Restructured command organization

### Fixed
- DNS record creation validation
- Configuration file path resolution
- Output formatting in table mode

## [0.1.0] - 2024-02-01

### Added
- Initial release
- Basic domain management (list, check, register, renew)
- DNS record management (retrieve, create, edit, delete)
- SSL certificate operations
- Configuration profile management
- Account information retrieval 