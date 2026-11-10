# FluxiBot 🤖

FluxiBot is a Python-based Twitch chat-controlled PTZ camera controller. It communicates with local DVR/NVR cameras using the **DVRIP (Sofia) protocol**.

Viewers can control camera movement directly through Twitch chat.

It was originally created for a [Konfluxus](konfluxus.org) livestream in 2026

## Features

- Twitch IRC chat integration (anonymous login)
- PTZ camera movement (8 directions)
- Camera zoom control
- Configurable movement boundaries
- User banning and command pausing
- Local admin console in Hungarian

## Requirements

- Python 3.10+
- DVRIP-compatible PTZ camera
- Target Twitch channel
- [python-dvr](https://github.com/OpenIPC/python-dvr)
- [Rich](https://github.com/Textualize/rich)

## Configuration

Configure your Twitch channel and camera credentials in the Python script:

```python
channel_name = "#yourchannel"

cam_ip = "192.168.1.123"
cam_username = "admin"
cam_password = "your_password"
```

Adjust `max_x` and `max_y` to configure the movement boundaries.

## Usage

Run the bot:

```bash
python fluxibot.py
```

Viewers can use these commands in Twitch chat:

| Command | Action |
|---|---|
| `up` | Move camera up |
| `down` | Move camera down |
| `left` | Move camera left |
| `right` | Move camera right |
| `zin` | Zoom in |
| `zout` | Zoom out |

Admin console commands:

| Command | Action |
|---|---|
| `h` | Show help |
| `pause` | Pause chat commands |
| `start` | Resume chat commands |
| `center` | Reset virtual camera position |
| `ban username` | Ban a chat user |

## License

See [LICENSE](LICENSE) for license information.
