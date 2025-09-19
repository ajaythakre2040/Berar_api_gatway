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
USER_STATUS = {
    1: "Active",
    2: "Inactive",
    3: "Suspended",
    4: "Pending",
    5: "Locked",
}