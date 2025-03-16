# Email Forwarding Cheat Sheet

This cheat sheet provides quick examples for common email forwarding tasks using the Porkbun CLI.

## Prerequisites

- Porkbun account with API access
- Domain registered with Porkbun
- API access enabled for your domain
- Porkbun CLI installed and configured

## Basic Commands

### List all email forwards for a domain

```bash
python -m porkbun.cli email list-forwards example.com
```

### Create a single email forward

Create a forward from `info@example.com` to `contact@example.com`:

```bash
python -m porkbun.cli email create-forward example.com info contact@example.com
```

### Update an existing email forward

Update the destination of a forward with ID `12345`:

```bash
python -m porkbun.cli email update-forward example.com 12345 new-email@example.com
```

### Delete an email forward

Delete a forward with ID `12345`:

```bash
python -m porkbun.cli email delete-forward example.com 12345
```

## Batch Operations

### Create multiple email forwards using JSON

First, create a JSON file with your email forwards:

```json
[
  {
    "email_prefix": "info",
    "forward_to": "contact@example.com"
  },
  {
    "email_prefix": "sales",
    "forward_to": "sales@example.com"
  },
  {
    "email_prefix": "support",
    "forward_to": "help@example.com"
  }
]
```

Then run the batch creation command:

```bash
python -m porkbun.cli email batch-create example.com email_forwards.json
```

### Delete multiple email forwards at once

```bash
python -m porkbun.cli email batch-delete example.com 12345 67890 54321
```

## Common Workflows

### Setting up standard business email forwards

Create a JSON file with common business email addresses:

```json
[
  {
    "email_prefix": "info",
    "forward_to": "main-contact@company.com"
  },
  {
    "email_prefix": "sales",
    "forward_to": "sales-team@company.com"
  },
  {
    "email_prefix": "support",
    "forward_to": "customer-support@company.com"
  },
  {
    "email_prefix": "billing",
    "forward_to": "accounts@company.com"
  },
  {
    "email_prefix": "careers",
    "forward_to": "hr@company.com"
  },
  {
    "email_prefix": "webmaster",
    "forward_to": "tech@company.com"
  }
]
```

Apply to your domain:

```bash
python -m porkbun.cli email batch-create example.com business_forwards.json
```

### Creating team member forwards

For a team where you want all team members to have email addresses:

```json
[
  {
    "email_prefix": "john.smith",
    "forward_to": "john.personal@gmail.com"
  },
  {
    "email_prefix": "jane.doe",
    "forward_to": "jane.personal@outlook.com"
  },
  {
    "email_prefix": "alex.jones",
    "forward_to": "alex.personal@yahoo.com"
  }
]
```

Apply with:

```bash
python -m porkbun.cli email batch-create example.com team_forwards.json
```

### Create functional role addresses

Set up role-based email addresses:

```json
[
  {
    "email_prefix": "ceo",
    "forward_to": "jane.doe@company.com"
  },
  {
    "email_prefix": "cto",
    "forward_to": "john.smith@company.com"
  },
  {
    "email_prefix": "marketing",
    "forward_to": "marketing-team@company.com"
  }
]
```

Apply with:

```bash
python -m porkbun.cli email batch-create example.com role_forwards.json
```

## Tips and Tricks

1. **Finding Forward IDs**: Use the `list-forwards` command to get the IDs needed for updating or deleting forwards.

2. **Organizing JSON Files**: Create separate JSON files for different types of forwards (roles, departments, individuals) to keep things organized.

3. **Backup Before Deleting**: Always list and save your current forwards before making batch deletions.

4. **Validation**: The CLI validates email formats, but you can use the `--help` flag to understand all requirements.

5. **Error Handling**: The CLI provides detailed error messages if something goes wrong with API access or if the domain is not properly configured.

## Troubleshooting

If you encounter any issues:

1. **API Access**: Ensure your domain has API access enabled in the Porkbun dashboard.

2. **Authentication**: Check that your API keys are correctly configured.

3. **Rate Limiting**: If you receive rate limit errors, space out your requests.

4. **Invalid Domain**: Make sure the domain is registered with Porkbun and spelled correctly.

5. **Email Format**: Ensure all email addresses follow standard format (user@domain.tld).

For more details on any command, use the `--help` flag:

```bash
python -m porkbun.cli email list-forwards --help
``` 