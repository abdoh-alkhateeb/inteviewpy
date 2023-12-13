import requests
import time
import json

MAILTM_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json" 
}

class MailTmError(Exception):
    pass

def _make_mailtm_request(request_fn, timeout = 600):
    tstart = time.monotonic()
    error = None
    status_code = None

    while time.monotonic() - tstart < timeout:
        try:
            r = request_fn()
            status_code = r.status_code

            if status_code == 200 or status_code == 201:
                return r.json()

            if status_code != 429:
                break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            error = e

        time.sleep(1.0)

    if error is not None:
        raise MailTmError(error) from error

    if status_code is not None:
        raise MailTmError(f"Status code: {status_code}")

    if time.monotonic() - tstart >= timeout:
        raise MailTmError("timeout")

    raise MailTmError("unknown error")

def get_mailtm_domains():
    def _domain_req():
        return requests.get("https://api.mail.tm/domains", headers = MAILTM_HEADERS)

    r = _make_mailtm_request(_domain_req)

    return [ x["domain"] for x in r ]

def create_mailtm_account(address, password):
    account = json.dumps({"address": address, "password": password})

    def _acc_req():
        return requests.post("https://api.mail.tm/accounts", data=account, headers=MAILTM_HEADERS)

    r = _make_mailtm_request(_acc_req)

    assert len(r["id"]) > 0

def get_mailtm_id(address, password):
    account = json.dumps({"address": address, "password": password})

    def _tkn_req():
        return requests.post("https://api.mail.tm/token", data=account, headers=MAILTM_HEADERS)

    r = _make_mailtm_request(_tkn_req)

    return r["id"]

def get_mailtm_token(address, password):
    account = json.dumps({"address": address, "password": password})

    def _tkn_req():
        return requests.post("https://api.mail.tm/token", data=account, headers=MAILTM_HEADERS)

    r = _make_mailtm_request(_tkn_req)

    return r["token"]

def get_mailtm_emails(token):
    headers = {"Authorization": f"Bearer {token}"}
    headers.update(MAILTM_HEADERS)

    def _ems_req():
        return requests.get("https://api.mail.tm/messages", headers=headers)

    r = _make_mailtm_request(_ems_req)

    return r

def get_mailtm_email(token, id):
    headers = {"Authorization": f"Bearer {token}"}
    headers.update(MAILTM_HEADERS)

    def _em_req():
        return requests.get(f"https://api.mail.tm/messages/{id}", headers=headers)

    r = _make_mailtm_request(_em_req)

    return r

def get_mailtm_emails_headers(token):
    r = get_mailtm_emails(token)

    return [{"from": item["from"], "to": item["to"], "subject": item["subject"], "date": item["createdAt"]} for item in r]

def get_mailtm_email_headers(token, id):
    r = get_mailtm_email(token, id)

    return {"from": r["from"], "to": r["to"], "subject": r["subject"], "date": r["createdAt"]}
