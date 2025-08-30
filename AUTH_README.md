# 🔐 Authentication System for Trading Dashboard

## Overview
The trading dashboard now includes a simple but effective authentication system to protect your trading data from unauthorized access.

## Features
- ✅ **Email/Password Login**: Simple credential-based authentication
- ✅ **Session Persistence**: Stay logged in during your browser session
- ✅ **Remember Me**: Optional persistent login across browser restarts
- ✅ **Secure Storage**: Passwords are hashed using SHA-256
- ✅ **Session Management**: Automatic logout and token management
- ✅ **Mobile Friendly**: Works seamlessly on mobile devices

## Default Credentials
```
Email: admin@trading.com
Password: admin123
```
**⚠️ Important**: Change these default credentials after first login!

## Quick Start

### 1. First Login
1. Run the dashboard: `streamlit run dashboard.py`
2. Use default credentials to login
3. Access the full trading dashboard
4. Change default credentials (see User Management below)

### 2. User Management
Use the included user management utility:
```bash
python user_manager.py
```

This allows you to:
- View all users
- Add new users
- Change passwords
- Manage user accounts

### 3. Security Features

#### Session Security
- Sessions expire after 30 days of inactivity
- Automatic logout on browser close (unless "Remember Me" is checked)
- Secure token-based authentication

#### Remember Me Feature
- Uses browser localStorage for persistence
- Tokens are automatically validated and refreshed
- Can be cleared by clicking "Logout"

## File Structure
```
data/
├── credentials.json    # User credentials (auto-created)
├── paper_portfolio.json # Your trading data
auth.py                 # Authentication system
user_manager.py         # User management utility
dashboard.py            # Main dashboard (now protected)
```

## Adding New Users

### Method 1: Using User Manager (Recommended)
```bash
python user_manager.py
# Select option 2 to add new user
```

### Method 2: Programmatic
```python
from auth import add_user

# Add a new user
add_user("newuser@example.com", "securepassword", "User Name")
```

## Security Considerations

### What This System Protects Against:
- ✅ Casual unauthorized access
- ✅ Accidental data exposure
- ✅ Basic access control needs

### What This System Does NOT Protect Against:
- ❌ Sophisticated attacks
- ❌ Server-side vulnerabilities
- ❌ Network traffic analysis
- ❌ Direct file system access

### Recommendations for Enhanced Security:
1. **Change default credentials immediately**
2. **Use strong passwords**
3. **Regular password updates**
4. **Secure your server/hosting environment**
5. **Use HTTPS in production**

## Configuration

### Session Duration
Default: 30 days. Change in `auth.py`:
```python
self.session_duration = 30  # days
```

### Credentials File Location
Default: `data/credentials.json`. Change in `auth.py`:
```python
def __init__(self, credentials_file="data/credentials.json"):
```

## Troubleshooting

### Login Issues
1. **"Invalid email or password"**: Check credentials are correct
2. **Can't access dashboard**: Ensure `auth.py` is in the same directory
3. **Remember me not working**: Check browser localStorage settings

### Reset System
To completely reset authentication:
1. Delete `data/credentials.json`
2. Restart the dashboard
3. System will recreate with default credentials

### Password Recovery
Currently, password recovery requires manual intervention:
1. Use `user_manager.py` to change password
2. Or manually edit `data/credentials.json`

## API Reference

### Main Functions
- `check_authentication()`: Verify if user is logged in
- `show_login_form()`: Display login interface
- `require_authentication(func)`: Decorator for protected functions

### User Management
- `add_user(email, password, name)`: Add new user
- `verify_credentials(email, password)`: Check login
- `create_session_token(email)`: Generate session token

## Best Practices

1. **Regular Updates**: Keep credentials current
2. **Monitor Access**: Check who has access periodically
3. **Backup Credentials**: Keep a secure backup of user data
4. **Use Strong Passwords**: Minimum 8 characters with mixed case
5. **Logout Properly**: Always use the logout button

## Example Usage

### Adding Multiple Users
```bash
python user_manager.py
# Add users for your team
```

### Custom Integration
```python
from auth import require_authentication

@require_authentication
def my_protected_function():
    # This function now requires login
    pass
```

## Support
For issues or questions about the authentication system, check:
1. This documentation
2. The `auth.py` file comments
3. The `user_manager.py` utility

---
**Note**: This authentication system is designed for personal/small team use. For production environments with sensitive data, consider implementing more robust security measures.
