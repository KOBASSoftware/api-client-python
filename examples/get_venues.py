#!/usr/bin/env python
"""Search for a customer"""
from kobas.Client import Client
from kobas.auth.Signer import Signer

signer = Signer(company_id=01234, identifier='sid:1', secret='API_SECRET')
client = Client(signer=signer)

client.ssl_verify_peer = False

venues = client.get('venue', {'fields': 'id,name'}, {})

print(venues)