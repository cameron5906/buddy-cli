def is_approval(response):
    """
    Check if a user input string is a yes or similar
    
    Returns:
        bool: Whether the response is an approval
    """
    
    approval_responses = {"y", "yes", "ok", "yeah", "sure", "okay", "yep", "yea"}
    return response.lower() in approval_responses


def is_denial(response):
    """
    Check if a user input string is a no or similar
    
    Returns:
        bool: Whether the response is a denial
    """
    
    denial_responses = {"n", "no", "nope", "nah"}
    return response.lower() in denial_responses
