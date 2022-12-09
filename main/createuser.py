from firebase_admin import auth

s=auth.create_user(
            display_name=self.display_name,
            email=self.email,
            email_verified=self.email_verified,
            phone_number=self.phone_number,
            password=self.password,
            disabled=self.disabled,
        )