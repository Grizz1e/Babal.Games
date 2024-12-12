import requests
import json

base_url = "https://a.khalti.com/api/v2"

def send_payment_request_to_khalti(amount, order_id, order_name, full_name, email):
    payload = json.dumps({
        "return_url": "http://127.0.0.1:8000/backend/verify_payment/",
        "website_url": "http://127.0.0.1:8000",
        "amount": amount["base_amount"] + amount["vat_amount"],
        "purchase_order_id": order_id,
        "purchase_order_name": order_name,
        "customer_info": {
            "name": full_name,
            "email": email,
        },
        "amount_breakdown": [
            {
                "label": "Mark Price",
                "amount": amount["base_amount"]
            },
            {
                "label": "VAT",
                "amount": amount["vat_amount"]
            }
        ],
    })
    url = f"{base_url}/epayment/initiate/"
    headers = {
        'Authorization': 'key live_secret_key_68791341fdd94846a146f0457ff7b455',
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)


def send_verification_request_to_khalti(pidx):
    payload = json.dumps({
        "pidx": pidx,
    })
    url = f"{base_url}/epayment/lookup/"
    headers = {
        'Authorization': 'key live_secret_key_68791341fdd94846a146f0457ff7b455',
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)

def get_steam_game_details(game_id=None):
    url = f"https://store.steampowered.com/api/appdetails?appids=1551360"
    response = requests.request("GET", url)
    return json.loads(response.text)