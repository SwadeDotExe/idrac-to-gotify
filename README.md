# idrac-to-gotify
A hacked-together SMTP → Gotify bridge built for Dell iDRAC systems that don't support TLS.

This project provides a small bridge that lets older iDRAC systems send their email alerts to Gotify. Many early iDRAC versions can only send plain, non-TLS SMTP, which makes it difficult to forward their alerts to modern services, such as [Mail2Gotify](https://github.com/MattMckenzy/Mail2Gotify). Even on the recent iDRAC9 that supports TLS, I am running the older 3.30.30 firmware so I can keep IPMI fan control, which means no TLS support.

This setup uses the excellent [alash3al/smtp2http](https://github.com/alash3al/smtp2http) container to receive the SMTP messages and a small translator service to format the alerts and send them on to Gotify. I have tested this with the iDRAC9 system, but it should work with older iDRAC versions as well.

## Setup

To get started, clone the repository and edit the `docker-compose.yml` file so it points to your Gotify server. The two variables you’ll need to update are:

```
GOTIFY_URL=https://your-gotify-address
GOTIFY_TOKEN=your-application-token
```

Once those are set, bring the containers up:

```
docker compose up -d --build
```

This starts two services:

* `smtp2http-idrac` — listens for plain SMTP on port 2525
* `translator` — formats the alert and sends it to your Gotify instance

Make sure port **2525** is reachable from the network where your iDRAC lives. You can change this port in the compose file if needed.

---

## iDRAC Configuration

On your iDRAC, go to the email alert settings and enter:

* **SMTP server:** the IP of the machine running this project
* **Port:** `2525`
* **Authentication:** **None**

The sender and recipient fields can be set to any valid-looking email addresses. The translator doesn’t use them; it simply looks at the message body.

After saving the settings, use the “Send Test Email” button. If everything is running correctly, you should see the email arrive in Gotify.

---

## AI Disclaimer
The translator component in this project was written with the assistance of AI. Please review the code before using it in your own environment and adjust it as needed for your setup.