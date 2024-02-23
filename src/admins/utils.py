def model_updated_response(success=True, msg=""):
    return {
        "status": "Success" if success else "Failed",
        "message": msg
    }
