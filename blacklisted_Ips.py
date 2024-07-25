import requests
import json
import ipaddress

# Replace these with your actual values
API_KEY = 'XXX'
MATTERMOST_WEBHOOK_URL = 'xxx'

# Function to check a network block
def check_network_block(network):
    url = 'https://api.abuseipdb.com/api/v2/check-block'
    querystring = {
        'network': str(network),
        'maxAgeInDays': '1',
    }
    headers = {
        'Accept': 'application/json',
        'Key': API_KEY
    }
    
    try:
        response = requests.request(method='GET', url=url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        decodedResponse = response.json()
#        print(f'Checked network: {network}, response: {json.dumps(decodedResponse, sort_keys=True, indent=4)}')  # Debug output
        
        for report in decodedResponse.get('data', {}).get('reportedAddress', []):
            ip_address = report.get('ipAddress')
            last_report = report.get('mostRecentReport')
            message = f'IP Address: {ip_address} has been blacklisted. Most recent report: {last_report}.\n https://www.abuseipdb.com/check/{ip_address}.' 
            send_mattermost_message(message)
    except requests.exceptions.RequestException as e:
        print(f'Error checking network {network}: {e}')
        if response is not None:
            print(f'Response content: {response.content}')  # Print response content if available

# Function to send a message to Mattermost
def send_mattermost_message(message):
    headers = {'Content-Type': 'application/json'}
    payload = {
        'text': message
    }
    try:
        response = requests.post(MATTERMOST_WEBHOOK_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an HTTPError for bad responses
        print(f'Message sent to Mattermost: {message}')  # Debug output
#        print(f'Mattermost response: {response.status_code}, {response.text}')  # Detailed logging
    except requests.exceptions.RequestException as e:
        print(f'Error sending message to Mattermost: {e}')
        if response is not None:
            print(f'Response content: {response.content}')  # Print response content if available

# Define the network ranges
network_ranges = [
    '127.0.0.1/8'  # Example /8 network
    # Add more networks as needed
]

# Loop through each network range
for net in network_ranges:
    network = ipaddress.ip_network(net)
    # Loop through each /24 subnet within the larger network
    for subnet in network.subnets(new_prefix=24):
        print(f'Checking network: {subnet}')  # Debug output
        check_network_block(subnet)
