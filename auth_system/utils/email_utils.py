# from django.core.mail import EmailMultiAlternatives
# from django.conf import settings
# from datetime import datetime


# def send_reset_password_email(to_email, reset_link):
#     subject = "Reset Your Password – Berar Finance"
#     from_email = settings.DEFAULT_FROM_EMAIL
#     year = datetime.now().year
#     timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")

#     text_content = f"""
# Hi {to_email},

# We received a request on {timestamp} to reset your password.

# Reset your password using this link:
# {reset_link}

# If you did not request this, please ignore the email.

# Thanks,
# Berar Finance Support Team
# """

#     html_content = f"""
# <html>
#   <body style="font-family: Arial, sans-serif; color: #333;">
#     <table width="100%" style="max-width: 600px; margin: auto; border-collapse: collapse;">
#       <tr>
#         <td style="padding: 20px; background-color: #f7f7f7; text-align: center;">
#           <h2 style="color: #004080;">Berar Finance</h2>
#         </td>
#       </tr>
#       <tr>
#         <td style="padding: 30px; background-color: #ffffff;">
#           <p>Hi {to_email},</p>
#           <p>We received a request on <strong>{timestamp}</strong> to reset your password.</p>
#           <p>Click the button below to reset your password:</p>
#           <p style="text-align: center; margin: 20px 0;">
#             <a href="{reset_link}" style="background-color: #004080; color: #fff; padding: 12px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
#           </p>
#           <p>If you didn’t request this, you can safely ignore this email.</p>
#           <p>Thanks,<br/>Berar Finance Support Team</p>
#         </td>
#       </tr>
#       <tr>
#         <td style="padding: 20px; background-color: #f0f0f0; text-align: center; font-size: 12px; color: #999;">
#           © {year} Berar Finance. All rights reserved.
#         </td>
#       </tr>
#     </table>
#   </body>
# </html>
# """

#     try:
#         msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
#         msg.attach_alternative(html_content, "text/html")
#         result = msg.send()
#         print(f"📤 Email successfully sent to {to_email} (result: {result})")
#     except Exception as e:
#         print(f"❌ Email send failed: {e}")


from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import datetime


def send_reset_password_email(to_email, reset_link):
    subject = "Reset your Berar Finance account password"
    from_email = f"Berar Finance <{settings.DEFAULT_FROM_EMAIL}>"
    year = datetime.now().year
    timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")

    # Plain text version
    text_content = f"""
Hi,

We received a request on {timestamp} to reset the password for your Berar Finance account.

Click the link below to reset it:
{reset_link}

If you didn’t request this, please ignore this email.

Thanks,
Berar Finance Support Team
"""

    # HTML version
    html_content = f"""
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 0 10px rgba(0,0,0,0.05);">
      <tr>
        <td style="background-color: #004080; color: #ffffff; padding: 20px; text-align: center;">
          <h2 style="margin: 0;">Berar Finance</h2>
        </td>
      </tr>
      <tr>
        <td style="padding: 30px;">
          <p style="font-size: 16px;">Hi,</p>
          <p style="font-size: 15px;">We received a request on <strong>{timestamp}</strong> to reset the password for your Berar Finance account.</p>
          <p style="font-size: 15px;">Click the button below to reset your password:</p>
          <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" style="background-color: #004080; color: #ffffff; padding: 14px 24px; text-decoration: none; border-radius: 6px; font-size: 16px;">
              Reset Password
            </a>
          </div>
          <p style="font-size: 14px;">If you didn’t request this, you can safely ignore this email.</p>
          <p style="font-size: 14px;">Thanks,<br/>Berar Finance Support Team</p>
        </td>
      </tr>
      <tr>
        <td style="background-color: #f0f0f0; color: #999; text-align: center; padding: 15px; font-size: 12px;">
          © {year} Berar Finance Pvt. Ltd.<br/>
          Contact: <a href="mailto:customercare@berarfinance.com" style="color: #555;">customercare@berarfinance.com</a>
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
