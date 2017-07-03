KOBAS API Client
=============

Signs API requests and allows interaction via cURL methods.

# Example

```python
# Setup

from kobas.Client import Client
from kobas.auth.Signer import Signer

signer = Signer(company_id=0, identifier='sid:?/imid:?', secret='...')
client = Client(signer=signer)

# Usage

customers = client.get('customer/search', {'email': 'example@example.com'}, {})

print(customers)
```

## Client Functions

## client.get(route = '', params = {}, headers = {})
cURL Get Request

## client.post(route = '', params = {}, headers = {})
cURL Post Request

## client.put(route = '', params = {}, headers = {})
cURL Put Request

## client.delete(route = '', params = {}, headers = {})
cURL Delete Request

## client.api_base_url = ''
Allows over-riding the base URL (only really needed for development)

## client.api_version = ''
Allows over-riding of the API version. Might be useful in future?

## ssl_verify_peer = false
Disables SSL Verify Peer. Needed for development, should never be used in production