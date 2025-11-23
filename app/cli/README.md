# Admin CLI Tool

Command-line utility for creating admin users for the CBT system.

## Usage

### Create Admin User

```bash
uv run python -m app.cli.create_admin
```

or

```bash
uv run python -m app.cli
```

### Interactive Prompts

The command will prompt you for:

1. **Username** - Must be unique
2. **Email** - Must be unique
3. **Password** - Hidden input (not echoed to screen)
4. **Confirm Password** - Must match

### Example

```bash
$ uv run python -m app.cli.create_admin
=== Create Admin User ===

Enter username: admin
Enter email: admin@cissa.com
Enter password: 
Confirm password: 

✅ Admin user created successfully!
   ID: 01234567-89ab-cdef-0123-456789abcdef
   Username: admin
   Email: admin@cissa.com
   Role: admin
   Created: 2025-11-23 23:15:00+00:00
```

## Features

- ✅ **Secure password input** - Uses `getpass` to hide password from terminal
- ✅ **Password confirmation** - Requires matching passwords
- ✅ **Duplicate checking** - Validates username and email are unique
- ✅ **Password hashing** - Uses bcrypt for secure password storage
- ✅ **Admin role** - Creates user with `role='admin'`
- ✅ **No StudentProfile** - Admin users don't have student profiles
- ✅ **Error handling** - Clear error messages for all failure cases

## Important Notes

- Admin users created via CLI have `role='admin'`
- Admin users do NOT have a StudentProfile (only students have profiles)
- Regular student registration via API automatically creates StudentProfile
- The password is securely hashed using bcrypt before storage

## Error Cases

The command will exit with an error if:

- Username already exists
- Email already exists
- Password is empty
- Passwords don't match
- Database connection fails
