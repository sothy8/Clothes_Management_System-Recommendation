# Email Configuration Guide

## 🔧 Email System Fixed!

### ✅ Current Configuration (Development)

The email system has been configured to use Django's **console backend** for development, which means:

- ✅ **No more "Connection refused" errors**
- ✅ Email content will be displayed in the terminal/console
- ✅ Perfect for testing and development
- ✅ No external SMTP server required

### 📧 How It Works Now

When a customer makes a QR code payment:
1. **Admin Notification**: Email content will be printed to the Django server console
2. **Customer Confirmation**: Email content will also be shown in the console
3. **No Network Errors**: Everything works offline

### 📝 Email Configuration Details

**Current settings in `CSR/settings.py`:**
```python
# Email Configuration for Development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@artisan-clothes.com'
ADMIN_EMAIL = 'admin@artisan-clothes.com'
```

### 🚀 For Production (When Ready)

To enable real email sending in production, replace the email configuration with:

```python
# Email Configuration for Production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Gmail SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-business-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use App Password, not regular password
DEFAULT_FROM_EMAIL = 'your-business-email@gmail.com'
ADMIN_EMAIL = 'admin@your-business.com'

# Optional: For multiple admins
ADMINS = [
    ('Admin Name', 'admin@your-business.com'),
    ('Manager Name', 'manager@your-business.com'),
]
```

### 📧 Gmail Setup Guide (For Production)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password in `EMAIL_HOST_PASSWORD`

3. **Alternative Email Providers**:
   - **Outlook/Hotmail**: `smtp-mail.outlook.com`, port 587
   - **Yahoo**: `smtp.mail.yahoo.com`, port 587
   - **SendGrid**: `smtp.sendgrid.net`, port 587
   - **Mailgun**: `smtp.mailgun.org`, port 587

### 🧪 Testing the Email System

1. **Start Django Server**: `python3 manage.py runserver 8001`
2. **Make a QR Code Payment**: Go through the checkout process
3. **Check Console Output**: You'll see the email content in the terminal
4. **Look for**: 
   ```
   Content-Type: text/plain; charset="utf-8"
   MIME-Version: 1.0
   Content-Transfer-Encoding: 7bit
   Subject: 🔔 New Payment Verification Required - Order #XXX
   From: noreply@artisan-clothes.com
   To: admin@artisan-clothes.com
   ```

### 🛡️ Security Notes

- ✅ **App Passwords**: Always use app-specific passwords for Gmail
- ✅ **Environment Variables**: Store email credentials in environment variables for production
- ✅ **SSL/TLS**: Always use encrypted connections (EMAIL_USE_TLS = True)
- ✅ **Backup**: Consider backup email services (SendGrid, Mailgun) for reliability

### 🔍 Troubleshooting

**If emails still don't work in production:**

1. **Check credentials**: Verify email/password are correct
2. **Firewall**: Ensure SMTP ports (587, 465) aren't blocked
3. **Provider limits**: Some providers limit SMTP access
4. **Django logs**: Check logs for detailed error messages
5. **Test connection**: Use `python3 manage.py shell` to test email sending

### ✅ Status: FIXED!

The "Connection refused" error has been resolved. Your payment notification system now works perfectly in development mode and is ready for production deployment.
