# Changelog

All notable changes to the Porkbun CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-03-16

### Added
- Service templates for domain setup (Cloudflare, Google Workspace, Office 365, Netlify, AWS, GitHub Pages, Vercel, Shopify, Digital Ocean, Firebase)
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