def is_approval(response):
    approval_responses = {"y", "yes", "ok", "yeah", "sure", "okay", "yep", "yea"}
    return response.lower() in approval_responses


def is_denial(response):
    denial_responses = {"n", "no", "nope", "nah"}
    return response.lower() in denial_responses
