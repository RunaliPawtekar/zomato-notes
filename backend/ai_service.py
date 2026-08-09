import json
import os

from dotenv import load_dotenv

load_dotenv()


def get_ai_response(user_message: str, system_prompt: str) -> str:

    if os.getenv("MOCK_AI", "1") != "1":
        raise NotImplementedError(
            "Real LLM path will be added later."
        )

    text = user_message.lower()

    # -------------------------
    # Payment Failure
    # -------------------------
    if (
        "payment" in text
        or "upi" in text
        or "transaction" in text
        or "failed" in text
    ):

        title = "Payment Failure"

        tags = [
            "payment",
            "upi",
            "transaction",
            "gateway"
        ]

    # -------------------------
    # Wrong Order
    # -------------------------
    elif (
        "instead of" in text
        or "wrong order" in text
        or "incorrect order" in text
    ):

        title = "Wrong Order"

        tags = [
            "order",
            "food",
            "item",
            "delivery"
        ]

    # -------------------------
    # Delivery Delay
    # -------------------------
    elif (
        "delay" in text
        or "late" in text
        or "traffic" in text
        or "delivered late" in text
    ):

        title = "Delivery Delay"

        tags = [
            "delivery",
            "delay",
            "rider",
            "traffic"
        ]

    # -------------------------
    # Refund
    # -------------------------
    elif "refund" in text:

        title = "Refund Issue"

        tags = [
            "refund",
            "payment",
            "customer"
        ]

    # -------------------------
    # Restaurant
    # -------------------------
    elif "restaurant" in text:

        title = "Restaurant Issue"

        tags = [
            "restaurant",
            "kitchen",
            "food"
        ]

    # -------------------------
    # Rider
    # -------------------------
    elif "rider" in text:

        title = "Rider Issue"

        tags = [
            "rider",
            "delivery",
            "location"
        ]

    # -------------------------
    # Cancellation
    # -------------------------
    elif "cancel" in text:

        title = "Order Cancellation"

        tags = [
            "cancel",
            "order",
            "customer"
        ]

    # -------------------------
    # Default
    # -------------------------
    else:

        title = "Customer Support Issue"

        tags = [
            "customer",
            "support",
            "issue"
        ]

    summary = " ".join(user_message.split()[:20])

    if not summary.endswith("."):
        summary += "..."

    return json.dumps({

        "title": title,

        "tags": tags,

        "summary": summary

    })