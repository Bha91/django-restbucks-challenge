from django.core.mail import send_mail

from django_restbucks_challenge.settings import EMAIL_SENDER_NOREPLAY


class Notify:
    def __init__(self):
        self.email_sender = EMAIL_SENDER_NOREPLAY

    def send_email(self, email_subject, email_body, sender, receivers):
        send_mail(email_subject, email_body, sender, receivers, fail_silently=False)


class ClientOrderStatusChange(Notify):
    def __init__(self):
        super().__init__()
        self.email_subject = 'Order state changed!'
        self.email_body = 'your order numbered {} has been changed from {} state to {}.\n Best\nRestBucks CoffeeShop'

    def send_email(self, receiver, order_id, previous_state, new_state):
        self.email_body = self.email_body.format(order_id, previous_state, new_state)
        super().send_email(self.email_subject, self.email_body, self.email_sender, [receiver])



