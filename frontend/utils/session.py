import jwt
import streamlit as st


def get_token():

    return st.session_state.get("access_token")


def get_claims():

    token = get_token()

    if not token:
        return {}

    try:
        claims = jwt.decode(
            token,
            options={
                "verify_signature": False,
                "verify_exp": False
            }
        )

        return claims

    except Exception:
        return {}


def get_roles():

    claims = get_claims()

    roles = claims.get("roles", [])

    if isinstance(roles, str):
        roles = [roles]

    return roles


def get_role():

    roles = get_roles()

    if "Administrator" in roles:
        return "Administrator"

    if "Student" in roles:
        return "Student"

    return None


def get_username():

    claims = get_claims()

    return (
        claims.get("preferred_username")
        or claims.get("upn")
        or claims.get("unique_name")
        or "User"
    )