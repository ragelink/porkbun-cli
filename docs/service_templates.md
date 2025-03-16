# Service Templates

The Porkbun CLI includes ready-to-use templates for setting up domains with popular services such as Cloudflare, Google Workspace, and Microsoft Office 365.

## Available Templates

The following templates are available in the `examples/templates` directory:

- **cloudflare_dns.json**: Standard DNS records for Cloudflare
- **google_workspace.json**: DNS configuration for Google Workspace (formerly G Suite)
- **office365.json**: DNS configuration for Microsoft Office 365
- **netlify.json**: DNS configuration for Netlify-hosted websites
- **aws_route53.json**: DNS configuration for AWS services
- **github_pages.json**: DNS configuration for GitHub Pages
- **vercel.json**: DNS configuration for Vercel deployments
- **shopify.json**: DNS configuration for Shopify e-commerce stores
- **digitalocean.json**: DNS configuration for Digital Ocean droplets
- **firebase.json**: DNS configuration for Firebase-hosted apps

## Using the Templates

You can use these templates with the `workflow setup-domain` command:

```bash
python -m porkbun.cli workflow setup-domain example.com --dns-records examples/templates/cloudflare_dns.json
```

### Important Notes

1. **Customization Required**: Some records in these templates need to be customized for your specific domain:
   - For Office 365: Replace the MX record `DOMAIN-com.mail.protection.outlook.com` with your domain-specific value (e.g., `example-com.mail.protection.outlook.com`)
   - For all templates: Update the DMARC email addresses to use your actual reporting email

2. **A Records**: The templates include placeholder A records that point to `192.0.2.1` (a reserved documentation IP). Update these to your actual web server IPs.

3. **Verification Records**: These templates don't include domain verification records (e.g., TXT records for Google or Microsoft verification). Add these manually after you initiate the setup with each provider.

## Template Modification

You can modify these templates for your specific needs:

1. Create a copy of a template:
   ```bash
   cp examples/templates/google_workspace.json myconfig.json
   ```

2. Edit the file with your customizations:
   ```bash
   nano myconfig.json
   ```

3. Apply the customized template:
   ```bash
   python -m porkbun.cli workflow setup-domain example.com --dns-records myconfig.json
   ```

## Batch Setup

You can set up a domain with multiple services at once using a batch file. The `examples/services_setup.yaml` file demonstrates this:

```bash
python -m porkbun.cli batch run examples/services_setup.yaml
```

Before running this batch file, make a copy and replace `DOMAIN` with your actual domain name:

```bash
sed 's/DOMAIN/example.com/g' examples/services_setup.yaml > my_setup.yaml
python -m porkbun.cli batch run my_setup.yaml
```

## Custom Service Templates

Creating your own service template is straightforward:

1. Create a JSON file with the required DNS records
2. Include all required record types (A, CNAME, MX, TXT, etc.)
3. Follow the format:
   ```json
   [
     {
       "type": "RECORD_TYPE",
       "name": "SUBDOMAIN",
       "content": "VALUE",
       "ttl": TTL_VALUE
     },
     ...
   ]
   ```

For services that require specific email forwards or URL forwards, create separate template files for these configurations and apply them with the appropriate commands. 

## Service-Specific Details

### Netlify

The Netlify template includes DNS records for hosting a website on Netlify:

- **A Record**: Points to Netlify's load balancer IP
- **CNAME Records**: For www, blog, and app subdomains, pointing to your Netlify app
- **SPF Record**: Includes Netlify and Mailgun mail servers
- **DMARC Record**: Basic DMARC policy
- **MX Records**: Configured for Mailgun email handling
- **ACME Challenge CNAME**: For Netlify's SSL certificate management

#### Custom Values to Replace:

- `DOMAIN.netlify.app`: Replace with your actual Netlify app domain
- `_netlify-site-verification`: Update with your Netlify verification code
- Email verification records: Add your specific verification codes from Mailgun

To apply with automatic customization:

```bash
python examples/setup_domain_services.py example.com --service netlify
```

### AWS Route 53

The AWS Route 53 template includes DNS records for various AWS services:

- **S3 Website Hosting**: CNAME record for www subdomain
- **API Gateway**: CNAME record for api subdomain
- **S3 Bucket**: CNAME record for static content
- **CloudFront Distributions**: CNAME records for CDN and environment-specific subdomains
- **SES (Simple Email Service)**: MX and verification records
- **SPF Record**: Includes Amazon SES mail servers
- **DMARC Record**: Basic DMARC policy

#### Custom Values to Replace:

- `REGION`: Your AWS region (e.g., us-east-1, eu-west-1)
- `_VERIFICATION_CNAME`: Your SES verification CNAME value
- Email verification records: Add your specific verification codes from SES

To apply with automatic customization:

```bash
python examples/setup_domain_services.py example.com --service aws --region us-west-2
```

### GitHub Pages

The GitHub Pages template includes DNS records for hosting a site on GitHub Pages:

- **A Records**: Four IP addresses for GitHub Pages
- **AAAA Records**: Four IPv6 addresses for GitHub Pages
- **CNAME Records**: For www, docs, and blog subdomains
- **GitHub Challenge TXT Record**: For domain verification
- **DMARC Record**: Basic DMARC policy

#### Custom Values to Replace:

- `USERNAME`: Your GitHub username (automatically replaced with domain prefix)
- `_github-pages-challenge-USERNAME`: Update with your GitHub verification code

To apply with automatic customization:

```bash
python examples/setup_domain_services.py example.com --service github
```

### Vercel

The Vercel template includes DNS records for hosting on Vercel:

- **A Record**: Points to Vercel's main IP
- **CNAME Records**: For www, api, app, docs, and admin subdomains
- **Wildcard CNAME**: For preview deployments
- **Vercel Verification TXT Record**: For domain verification
- **SPF and DMARC Records**: For email validation
- **MX Records**: For Vercel email handling

#### Custom Values to Replace:

- `_vercel`: Update with your Vercel verification code

To apply with automatic customization:

```bash
python examples/setup_domain_services.py example.com --service vercel
```

### Shopify

The Shopify template includes DNS records for setting up an e-commerce store with Shopify:

- **A Record**: Points to Shopify's IP address
- **CNAME Records**: For www, cdn, checkout, assets, and shop subdomains
- **Shopify Verification TXT Record**: For domain verification
- **SPF and DMARC Records**: For email validation
- **MX Record**: For Shopify email handling

#### Custom Values to Replace:

- `SHOPIFY_SUBDOMAIN`: Your Shopify store subdomain (automatically replaced with domain-hyphenated)
- `shopify-verification`: Update with your Shopify verification code

To apply with automatic customization:

```bash
python examples/setup_domain_services.py example.com --service shopify
```

### Digital Ocean

The Digital Ocean template includes DNS records for hosting on Digital Ocean:

- **A Records**: For primary domain and www (pointing to your Droplet IP)
- **CNAME Records**: For various subdomains and environments
- **DigitalOcean Verification TXT Record**: For domain verification
- **SPF and DMARC Records**: For email validation
- **MX Records**: For Digital Ocean email handling
- **Spaces CNAME Record**: For Digital Ocean Spaces object storage

#### Custom Values to Replace:

- `DROPLET_IP`: Replace with your actual Droplet's IP address
- `do-verification`: Update with your Digital Ocean verification code

To apply with automatic customization:

```bash
python examples/setup_domain_services.py example.com --service digitalocean --droplet-ip 104.248.112.123
```

### Firebase

The Firebase template includes DNS records for hosting a web app on Firebase:

- **A Records**: Points to Firebase hosting IP addresses
- **CNAME Records**: For www, app, api, and other subdomains
- **Firebase Verification TXT Record**: For domain verification
- **SPF and DMARC Records**: For email validation
- **MX Records**: For Google mail handling (Firebase uses Google services)

#### Custom Values to Replace:

- `FIREBASE_APP_ID`: Your Firebase project ID (automatically replaced with domain-hyphenated)
- `firebase`: Update with your Firebase verification code
- `google-site-verification`: Update with your Google verification code

To apply with automatic customization:

```bash
python examples/setup_domain_services.py example.com --service firebase
``` 