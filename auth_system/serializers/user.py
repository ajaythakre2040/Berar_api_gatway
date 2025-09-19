import re
from rest_framework import serializers
from auth_system.models.user import TblUser
from auth_system.models.role import Role  # Ensure Role is imported


class TblUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role_type = serializers.CharField(source="role_id.type", read_only=True)

    class Meta:
        model = TblUser
        fields = [
            "id",
            "role_id",
            "role_type",
            "status",
            "first_name",
            "last_name",
            "mobile_number",
            "email",
            "username",
            "is_active",
            "key",
            "timeout",
            "department",
            "position",
            "created_by",
            "updated_by",
            "deleted_by",
            "created_at",
            "updated_at",
            "deleted_at",
            "password",
        ]
        read_only_fields = [
            "id",
            "key",
            "created_at",
            "updated_at",
            "deleted_at",
            "created_by",
            "updated_by",
            "deleted_by",
            "role_type",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = TblUser.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def validate_mobile_number(self, value):
        if not re.match(r"^\d{10}$", value):
            raise serializers.ValidationError(
                "Mobile number must be exactly 10 digits."
            )
        return value

    def validate_password(self, value):
        errors = []
        if len(value) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", value):
            errors.append("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            errors.append("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", value):
            errors.append("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            errors.append("Password must contain at least one special character.")

        if errors:
            raise serializers.ValidationError(errors)

        return value
