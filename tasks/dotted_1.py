from dotted.collection import DottedDict

def get_user_street_name(user: DottedDict) -> str:
    """Retrieve the street name of the user. The user has the following JSON schema:
    {
        name: str,
        age: int,
        email: str,
        street: {
            number: int,
            name: str
        }
    }
    """
    return user["street.name"]