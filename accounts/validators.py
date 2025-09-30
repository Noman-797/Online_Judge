from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


class MixedPasswordValidator:
    """
    Validate that the password contains mixed characters (letters + numbers/symbols)
    """
    
    def validate(self, password, user=None):
        has_letter = re.search(r'[a-zA-Z]', password)
        has_number_or_symbol = re.search(r'[\d!@#$%^&*(),.?":{}|<>]', password)
        
        if not (has_letter and has_number_or_symbol):
            raise ValidationError(
                _("Password must contain both letters and numbers/symbols."),
                code='password_not_mixed',
            )

    def get_help_text(self):
        return _("Your password must contain both letters and numbers/symbols.")