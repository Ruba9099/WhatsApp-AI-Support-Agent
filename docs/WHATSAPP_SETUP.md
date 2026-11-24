# Connecting a real WhatsApp number (Meta Cloud API)

You need the app running on a public **HTTPS** URL first (see [DEPLOY_AWS.md](DEPLOY_AWS.md)).
Meta will not accept plain `http://` webhooks.

## Steps
1. Go to <https://developers.facebook.com/apps> → **Create app** → type **Business**.
2. Add the **WhatsApp** product. Meta gives you a free test phone number.
3. In **WhatsApp → API Setup**, copy:
   - **Temporary access token** → `WHATSAPP_TOKEN`
   - **Phone number ID** → `WHATSAPP_PHONE_NUMBER_ID`
4. Add your own phone under **To** as a test recipient and confirm the code.
5. In **App settings → Basic**, copy **App secret** → `WHATSAPP_APP_SECRET`.
6. Pick any random string for `WHATSAPP_VERIFY_TOKEN` and put it in `.env`. Restart the app.
7. In **WhatsApp → Configuration → Webhook**, click **Edit**:
   - Callback URL: `https://YOUR-DOMAIN/webhook`
   - Verify token: the same string as step 6
   - Click **Verify and save**. Meta calls `GET /webhook`; you should see it succeed.
8. Under **Webhook fields**, subscribe to **messages**.
9. Send "What are your timings?" from your phone to the test number. You'll get the AI reply.

## Going live
- The temporary token expires in 24 hours. For production create a **System User** in
  Meta Business Settings and generate a **permanent token**.
- Add a real business phone number and complete business verification.
- Remember the 24-hour rule: free-form replies are allowed only within 24 hours of the
  customer's last message. Outside that window you need approved message templates.

## Optional: HubSpot
1. HubSpot → **Settings → Integrations → Private Apps → Create**.
2. Scopes: `crm.objects.contacts.write` and `crm.objects.contacts.read`.
3. Copy the token → `HUBSPOT_TOKEN`. New WhatsApp customers now appear as leads.
