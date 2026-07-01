#!/usr/bin/env python3
"""Bulk domain availability checker with rate limiting."""
import time
import sys

# NOTE: This script is currently non-functional against the current codebase
# (PorkbunAPI/check_domain/dict-style profile no longer exist). Prefer the
# working `bulk_check.sh` or the CLI's `domains check` command. Kept only as a
# reference; needs a rewrite against porkbun.api.make_request before use.
from porkbun.api import PorkbunAPI
from porkbun.config import ConfigManager

def check_domains(domains: list[str]):
    config = ConfigManager()
    profile = config.get_default_profile()
    if not profile:
        print("Error: no default Porkbun profile configured. Run 'porkbun config init' first.")
        sys.exit(1)
    api = PorkbunAPI(profile['api_key'], profile['secret_key'])
    
    available = []
    taken = []
    
    for i, domain in enumerate(domains):
        if i > 0:
            time.sleep(11)  # Rate limit: 1 check per 10 seconds
        
        try:
            result = api.check_domain(domain)
            if result.get('avail') == 'yes':
                price = result.get('price', '?')
                available.append((domain, price))
                print(f"✅ {domain} - ${price}/yr")
            else:
                taken.append(domain)
                print(f"❌ {domain} - taken")
        except Exception as e:
            print(f"⚠️  {domain} - error: {e}")
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"\n✅ AVAILABLE ({len(available)}):")
    for domain, price in available:
        print(f"   {domain} - ${price}/yr")
    print(f"\n❌ TAKEN ({len(taken)}):")
    for domain in taken:
        print(f"   {domain}")

if __name__ == "__main__":
    domains = sys.argv[1:]
    if not domains:
        print("Usage: python bulk_check.py domain1.com domain2.com ...")
        sys.exit(1)
    check_domains(domains)
