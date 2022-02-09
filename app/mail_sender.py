from requests import post
from os import environ
import json


def get_register_body() -> dict:
    return {
        "subject": "新規登録フォームの送信",
        "message": f"下記のURLから新規登録を行なってください。\n"
    }


def get_confirm_register_body() -> dict:
    return {
        "subject": "新規登録完了",
        "message": "Find Flightsをご利用いただきありがとうございます。\n"
                   "新規登録が完了しました。"
    }


def get_update_email_body() -> dict:
    return {
        "subject": "メールアドレスの更新",
        "message": "Find Flightsをご利用いただきありがとうございます\n"
                   "下記のURLにアクセスしていただくことでメールアドレスの更新が完了します。\n"
    }


class EmailSender(object):
    def __init__(self, recipient: str, action: str, URL: str):
        self.api_key = environ.get("MAIL_API_KEY")
        self.domain_name = environ.get("MAIL_DOMAIN_NAME")
        self.recipient = recipient
        if action == "pre_register":
            self.body = get_register_body()
        elif action == "update_email":
            self.body = get_update_email_body()
        elif action == "confirm_register":
            self.body = get_confirm_register_body()

        self.URL = URL

    def append_URL_to_body(self):
        self.body["message"] += self.URL

    def send(self) -> (int, str):
        if self.URL:
            self.append_URL_to_body()
        response = post(
            url=f"https://api.mailgun.net/v3/{self.domain_name}/messages",
            auth=("api", self.api_key),
            data={
                "from": f"Find Flights管理者 <customer_srvice@{self.domain_name}>",
                "to": self.recipient,
                "subject": self.body["subject"],
                "text": self.body["message"]
            }
        )
        status_code = response.status_code
        response_message = json.loads(response.text)["message"]
        return status_code, response_message
