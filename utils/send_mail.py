from typing import List
from fastapi import FastAPI
from fastapi_mail import ConnectionConfig,FastMail,MessageSchema,MessageType,NameEmail
from pydantic import BaseModel
from starlette.responses import JSONResponse
import logging


conf=ConnectionConfig(
    MAIL_USERNAME="saleemkhurram1234@gmail.com",
    MAIL_PASSWORD="zzlx ivfz gzad izzp",
    MAIL_FROM="saleemkhurran1234@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="LMS-PYTHON-DEVELOPMENT",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_email(emails:List[str],title:str,otp:str=None):
    if otp:
        body_html=f"""
                Dear User,<br><br>
                Use the code below to reset your password:
                <span style="display:block;margin:20px 0;font-size:32px;letter-spacing:8px;font-weight:bold;color:#1e3a8a;text-align:center;">{otp}</span>
                This code expires in 10 minutes. If you did not request it, please ignore this email."""
    else:
        body_html=f"""
                Dear Student,<br><br>
                This is to confirm that your request has been processed successfully:
                <strong>{title}</strong>.<br><br>
                Please log in to your LMS portal to view the details and current status."""

    html=f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background-color:#f3f4f6;font-family:Arial,Helvetica,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f4f6;padding:24px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:8px;overflow:hidden;">
          <tr>
            <td style="background-color:#1e3a8a;padding:24px 32px;">
              <h1 style="margin:0;color:#ffffff;font-size:20px;">LMS Portal</h1>
            </td>
          </tr>
          <tr>
            <td style="padding:32px;">
              <h2 style="margin:0 0 16px 0;color:#111827;font-size:18px;">{title}</h2>
              <p style="margin:0;color:#374151;font-size:15px;line-height:1.6;">{body_html}
              </p>
              <p style="margin:24px 0 0 0;color:#374151;font-size:15px;line-height:1.6;">
                Regards,<br><strong>LMS Support Team</strong>
              </p>
            </td>
          </tr>
          <tr>
            <td style="background-color:#f9fafb;padding:16px 32px;border-top:1px solid #e5e7eb;">
              <p style="margin:0;color:#9ca3af;font-size:12px;line-height:1.5;">
                This is an automated message, please do not reply to this email.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    message=MessageSchema(
        subject=title,
        recipients=emails,
        body=html,
        subtype=MessageType.html
    )
    fm=FastMail(conf)
    await fm.send_message(message)
    logging.info(f"Email sent to {emails}")
    return {"message":"Email has been sent successfully"}