def generate_tags(text: str):

    text = text.lower()

    # Login
    if any(word in text for word in [
        "login", "log in", "signin", "otp", "password"
    ]):
        return "login"

    # Coupon
    if "discount coupon" in text or "coupon" in text:
        return "coupon"

    # Payment / Refund
    if any(word in text for word in [
        "payment", "upi", "gateway", "transaction", "refund", "charged twice"
    ]):
        return "payment"

    # Delivery
    if any(word in text for word in [
        "delivery", "rider", "traffic", "late"
    ]):
        return "delivery"

    # Order / Restaurant
    if any(word in text for word in [
        "order", "restaurant", "biryani", "cancelled", "cancel"
    ]):
        return "order"

    # Customer
    if any(word in text for word in [
        "customer", "complaint", "user"
    ]):
        return "customer"

    return "general"