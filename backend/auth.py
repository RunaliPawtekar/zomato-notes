from fastapi import Header, HTTPException


def verify_token(x_token: str = Header(...)):

    if x_token != "zomato123":

        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token"
        )