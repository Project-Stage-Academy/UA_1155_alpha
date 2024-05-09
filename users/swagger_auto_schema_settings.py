from drf_yasg import openapi

# LoginAPIView swagger settings

loginAPIView_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["email", "password"],
    properties={
        "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        "password": openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD
        ),
    },
    example={
        "email": "testforum97@gmail.com",
        "password": "Password123!",
    },
)

loginAPIView_responses = {
    200: openapi.Response(
        description="User created successfully",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={
            "application/json": {
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            },
        },
    ),
    400: openapi.Response(
        description="User not found",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={
            "application/json": {
                "message": "User not found",
            },
        },
    ),
    401: openapi.Response(
        description="Wrong password",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={
            "application/json": {
                "message": "Wrong password",
            },
        },
    ),
}


# LogoutAPIView swagger settings

logoutAPIView_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["refresh"],
    properties={
        "refresh": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="The refresh token to be invalidated.",
        )
    },
    example={"refresh": "your_refresh_token_here"},
)

logoutAPIView_responses = {
    200: openapi.Response(
        description="Successful exit",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={
            "application/json": {
                "success": "Successful exit",
            },
        },
    ),
    400: openapi.Response(
        description="Bad request",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={"application/json": {"error": "Refresh token is required."}},
    ),
}


# UserRegisterAPIView swagger settings

userRegisterAPIView_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        "first_name": openapi.Schema(type=openapi.TYPE_STRING),
        "last_name": openapi.Schema(type=openapi.TYPE_STRING),
        "password": openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD
        ),
        "password2": openapi.Schema(
            type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD
        ),
        "profile_img_url": openapi.Schema(type=openapi.TYPE_STRING),
        "is_active_for_proposals": openapi.Schema(type=openapi.TYPE_BOOLEAN),
    },
    required=["email", "first_name", "last_name", "password", "password2"],
    example={
        "email": "testforum97@gmail.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "Password123!",
        "password2": "Password123!",
        "profile_img_url": "string",
        "is_active_for_proposals": True,
    },
)

userRegisterAPIView_responses = {
    201: openapi.Response(
        description="User created successfully",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={
            "application/json": {
                "User name": "John",
                "message": "User created successfully",
            }
        },
    ),
    400: openapi.Response(
        description="Bad request",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={"application/json": {"email": ["Enter a valid email address."]}},
    ),
    500: openapi.Response(
        description="Internal Server Error",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={"application/json": {"message": "Internal Server Error"}},
    ),
}


# SendEmailConfirmationAPIView swagger settings

sendEmailConfirmationAPIView_responses_GET = {
    200: openapi.Response(
        description="Plese, confifm your email",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={"application/json": {"message": "Plese, confifm your email"}},
    ),
}

sendEmailConfirmationAPIView_responses_POST = {
    200: openapi.Response(
        description="Sucsess",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={"application/json": {"message": "Email verified successfully"}},
    ),
    400: openapi.Response(
        description="Incorrect token",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={"application/json": {"error": "Invalid token"}},
    ),
    403: openapi.Response(
        description="Retrying to verify email",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={"application/json": {"message": "Email already verified"}},
    ),
    404: openapi.Response(
        description="User not found",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={"application/json": {"error": "Invalid user ID"}},
    ),
}


# PasswordResetRequest swagger settings

passwordResetRequest_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["email"],
    properties={
        "email": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_EMAIL,
        )
    },
    example={"email": "testforum97@gmail.com"},
)

passwordResetRequest_responses = {
    200: openapi.Response(
        description="Successfully sent password reset email",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={
            "application/json": {"message": "Password reset email sent"},
        },
    ),
    400: openapi.Response(
        description="No email",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={"application/json": {"error": "Email is required"}},
    ),
    404: openapi.Response(
        description="Incorrect email",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={"application/json": {"error": "User with this email does not exist"}},
    ),
}


# PasswordResetConfirm swagger settings

passwordResetConfirm_responses = {
    200: openapi.Response(
        description="Password reset successfully",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={
            "application/json": {"message": "Password reset successfully"},
        },
    ),
    400: openapi.Response(
        description="Invalid token",
        schema=openapi.Schema(type=openapi.TYPE_OBJECT),
        examples={
            "application/json": {
                "error": "Invalid token",
                "Error": "Password must contain at least 8 characters, one letter, one number and one special character",
            }
        },
    ),
}
