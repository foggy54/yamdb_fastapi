class Role:
    """
    Constants for the various roles scoped in the application ecosystem
    """

    GUEST = {
        "name": "guest",
        "description": "A Guest Account",
    }
    USER = {
        "name": "user",
        "description": "Primary Administrator/Superuser For an Account",
    }

    MODERATOR = {
        "name": "moiderator",
        "description": "Day to Day Administrator of Events For an Account",
    }
    ADMIN = {
        "name": "admin",
        "description": "Admin of Application Ecosystem",
    }
    SUPER_ADMIN = {
        "name": "super_admin",
        "description": "Super Administrator of Application Ecosystem",
    }
