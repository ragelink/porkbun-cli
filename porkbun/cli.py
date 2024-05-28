import click
from porkbun.commands import domains, dns, ssl, email, account, whois

@click.group()
def cli():
    """Porkbun CLI"""
    pass

cli.add_command(domains.domains)
cli.add_command(dns.dns)
cli.add_command(ssl.ssl)
cli.add_command(email.email)
cli.add_command(account.account)
cli.add_command(whois.whois)

def main():
    cli()

if __name__ == "__main__":
    main()