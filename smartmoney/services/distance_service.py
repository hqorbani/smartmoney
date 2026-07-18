from smartmoney.models.signal import Signal


class DistanceService:
    """
    Calculates the distance between the current market
    price and the signal zone.
    """

    def calculate(
        self,
        signal: Signal,
        current_price: float,
    ) -> Signal:

        signal.current_price = current_price

        # -----------------------------
        # اگر قیمت داخل ناحیه باشد
        # -----------------------------

        if signal.price_low <= current_price <= signal.price_high:

            signal.distance = 0.0

            return signal

        # -----------------------------
        # پایین ناحیه
        # -----------------------------

        if current_price < signal.price_low:

            signal.distance = (
                signal.price_low - current_price
            )

            return signal

        # -----------------------------
        # بالای ناحیه
        # -----------------------------

        signal.distance = (
            current_price - signal.price_high
        )

        return signal