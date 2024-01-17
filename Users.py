import re


class Users:
    def __init__(self, username, email, psw, repeat_psw):
        self.__username = username
        self.__email = email
        self.__psw = psw
        self.__repeat_psw = repeat_psw

    def get_username(self):
        return self.__username

    def get_email(self):
        return self.__email

    def get_psw(self):
        return self.__psw

    def get_repeat_psw(self):
        return self.__repeat_psw

    def is_valid_password(self, password):
        # Define the password requirements
        min_length = 8
        requires_uppercase = True
        requires_lowercase = True
        requires_digit = True
        requires_special = True
        forbidden_patterns = ['password', '123456', 'qwerty']  # Add more if necessary

        # Check the length requirement
        if len(password) < min_length:
            return False

        # Check uppercase requirement
        if requires_uppercase and not re.search(r'[A-Z]', password):
            return False

        # Check lowercase requirement
        if requires_lowercase and not re.search(r'[a-z]', password):
            return False

        # Check digit requirement
        if requires_digit and not re.search(r'\d', password):
            return False

        # Check special character requirement
        if requires_special and not re.search(r'[!@#$%^&*]', password):
            return False

        # Check forbidden patterns
        for pattern in forbidden_patterns:
            if re.search(pattern, password, re.IGNORECASE):
                return False

        return True


