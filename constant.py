ADMIN_USER = {
    "first_name": "Admin",
    "last_name": "User",
    "email": "admin@gmail.com",
    "mobile_number": "1234567890",
    "username": "admin",            # required
    "password": "Admin@123",
    "position": "System Admin",
    "role_id": 1,                   # must exist in Role table
    "department_id": 1           # or a valid department ID
}
# Status codes as integers
STATUS_ACTIVE = 1
STATUS_INACTIVE = 2
STATUS_SUSPENDED = 3
STATUS_PENDING = 4
STATUS_LOCKED = 5

# Optional mapping for labels (sirf display ke liye)
USER_STATUS = {
    STATUS_ACTIVE: "Active",
    STATUS_INACTIVE: "Inactive",
    STATUS_SUSPENDED: "Suspended",
    STATUS_PENDING: "Pending",
    STATUS_LOCKED: "Locked",
}

# Choices tuple for Django model
USER_STATUS_CHOICES = tuple(USER_STATUS.items())