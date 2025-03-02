import string

def password_strength(password):
    length = len(password) >= 12
    lowercase = any(c.islower() for c in password)
    uppercase = any(c.isupper() for c in password)
    number = any(c.isdigit() for c in password)
    special = any(c in string.punctuation for c in password)
    common_passwords = {
        "password", "123456", "123456789", "12345678", "12345", "1234567", "qwerty", 
        "abc123", "letmein", "monkey", "iloveyou", "trustno1", "dragon", "baseball", 
        "football", "starwars", "123123", "welcome", "admin", "password1", 
        "qwertyuiop", "123321", "superman", "1q2w3e4r", "sunshine", "ashley", 
        "bailey", "passw0rd", "shadow", "master"
    }

    if password in common_passwords:
        return "Very Weak"

    conditions_met = sum([length, lowercase, uppercase, number, special]) 

    if conditions_met == 5: 
        return "Very Strong"
    elif conditions_met >= 4: 
        return "Strong"
    else:
        return "Weak"

password = input("Enter password: ")
print(password_strength(password))