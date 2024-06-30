from django.contrib.auth.tokens import PasswordResetTokenGenerator


class OrderConfirmationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, order, timestamp):
        return str(order.pk) + str(timestamp) + str(order.status)

order_confirmation_token = OrderConfirmationTokenGenerator()
