# docker-status-check

It checks if your docker containers are running or not, and gives a warning on Discord.
You can change it to send a message to Slack, Telegram, or whatever you want.

Hell, I'll do it one day.

## Installation

Just clone it, it's a python script.

Well... You just need two things.

## Dependencies

- Docker
- Python 3

There, that's it.

## Usage

First, you need to set up your Discord webhook.
Use environment variables to set it up.

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

Or, hardcode it in the script (don't forget to remove it before `git push`ing it).

```python
class CONFIG:

    # Discord
    DISCORD_WEBHOOK_URL = os.environ.get(
        "DISCORD_WEBHOOK_URL",
        "https://discord.com/api/webhooks/...",
    )
```

Then you can run the script.
As the script has a hashbang, you can just run it.

```bash
chmod +x ./dcheck.py && ./dcheck.py
```

Or do the boring way.

```bash
python3 dcheck.py
```

Lots of options, huh?

## License

MIT

Or idk, do whatever you want with it.

## Contributing

Just open a PR.

## Support

If you have any questions, feel free to open an issue.

## Authors

- [ApplBoy (me)](https://github.com/ApplBoy)
