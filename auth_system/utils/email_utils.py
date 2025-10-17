from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import datetime


def send_reset_password_email(to_email, reset_link):
    subject = "Reset your Berar Finance account password"
    from_email = f"Berar Finance <{settings.DEFAULT_FROM_EMAIL}>"
    year = datetime.now().year
    timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")

    text_content = f"""
Hi,

We received a request on {timestamp} to reset the password for your Berar Finance account.

Click the link below to reset it:
{reset_link}

If you didn’t request this, please ignore this email.

Thanks,
Berar Finance Support Team
"""

    html_content = f"""
<html>
  <body style="font-family: Arial, sans-serif; background-color: 
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: auto; background-color: 
      <tr>
        <td style="background-color: 
          <h2 style="margin: 0;">Berar Finance</h2>
        </td>
      </tr>
      <tr>
        <td style="padding: 30px;">
          <p style="font-size: 16px;">Hi,</p>
          <p style="font-size: 15px;">We received a request on <strong>{timestamp}</strong> to reset the password for your Berar Finance account.</p>
          <p style="font-size: 15px;">Click the button below to reset your password:</p>
          <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" style="background-color: 
              Reset Password
            </a>
          </div>
          <p style="font-size: 14px;">If you didn’t request this, you can safely ignore this email.</p>
          <p style="font-size: 14px;">Thanks,<br/>Berar Finance Support Team</p>
        </td>
      </tr>
      <tr>
        <td style="background-color: 
          © {year} Berar Finance Pvt. Ltd.<br/>
          Contact: <a href="mailto:customercare@berarfinance.com" style="color: 
        </td>
      </tr>
    </table>
  </body>
</html>
"""

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email],
        )
        msg.attach_alternative(html_content, "text/html")
        result = msg.send()
        print(f"📤 Email successfully sent to {to_email} (result: {result})")
    except Exception as e:
        print(f"❌ Email send failed: {e}")
