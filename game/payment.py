import requests
import json

url = "https://a.khalti.com/api/v2/epayment/initiate/"
headers = {
    'Authorization': 'key test_secret_key_4cbdc98638fb4d8486703e771b6b86ce',
    'Content-Type': 'application/json',
}
def send_payment_request_to_khalti(return_url, amount, order_id, order_name):
    payload = json.dumps({
        "return_url": return_url,
        "website_url": "https://babal.games",
        "amount": int(amount),
        "purchase_order_id": str(order_id),
        "purchase_order_name": order_name,
    })

    response = requests.request("POST", url, headers=headers, data=payload)

    return response