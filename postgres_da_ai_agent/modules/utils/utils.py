from datetime import datetime

def in_termination_msg(content):
    have_content = content.get("content", None) is not None
    if have_content and "APPROVED" in content["content"]:
        return True
    return False

def get_date():
    return datetime.now().strftime("%Y_%m_%d_%H:%M:%S")