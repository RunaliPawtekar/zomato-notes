# tag_generator.py

def generate_tags(text: str):

    text = text.lower()

    keywords = {

        "payment": ["payment", "upi", "refund", "gateway", "transaction"],
        "order": ["order", "delivery", "restaurant", "cancel"],
        "customer": ["customer", "user", "complaint"],
        "login": ["login", "signin", "password", "otp"],
        "database": ["database", "sql", "db"],
        "server": ["server", "api", "backend", "timeout"],
        "app": ["app", "android", "ios", "mobile"],
        "network": ["network", "internet", "connection"]

    }

    tags = []

    for tag, words in keywords.items():

        for word in words:

            if word in text:

                tags.append(tag)

                break

    if not tags:

        tags.append("general")

    return ",".join(tags)