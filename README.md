# syslog-sms
Monitor syslog and send a push notification when something interesting happens. The name is outdated, this used to use Twilio to send SMS, but push notifications is way more affordable and flexible.

## Dependencies

- python3
- python3 requests
- systemd
- [Pushover](https://pushover.net/)

## Installation

### Install syslog-sms and Dependencies

#### Debian/Ubuntu/apt Based Distributions
```
sudo apt install python3 python3-pip python3-requests git
sudo mkdir /opt/syslog-sms
sudo git clone https://github.com/dhminch/syslog-sms.git /opt/syslog-sms
sudo cp /opt/syslog-sms/syslog-sms.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable syslog-sms
```

#### RHEL/CentOS/yum Based Distributions:

```
sudo yum install python3 python3-pip python3-requests git
sudo mkdir /opt/syslog-sms
sudo git clone https://github.com/dhminch/syslog-sms.git /opt/syslog-sms
sudo cp /opt/syslog-sms/syslog-sms.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable syslog-sms
```

### Configure syslog-sms

```
sudo cp /opt/syslog-sms/config.json.template /opt/syslog-sms/config.json
```

Edit config.json to suit your needs. The configurable fields are:

| Field | Description |
| --- | --- |
| `logs` | Comma separated list of files to monitor. Each file should be in quotes. |
| `monitor_frequency` | How often, in seconds, the log files should be checked for updates. 30-60 seconds is a good value. |
| `limits` - `host_cooldown` | How long, in seconds, to wait to send another alarm for a particular host (to avoid spamming you). |
| `limits` - `max_per_hour` | Max number of alarms to send in an hour (to avoid spamming you and keep costs down). |
| `limits` - `max_per_day` | Max number of alarms to send in a day (to avoid spamming you and keep costs down). |
| `pushover` - `app_token` | Your Pushover Application Token (on your Pushover Dashboard) |
| `pushover` - `target_token` | Your Pushover Target User or Group Token (on your Pushover Dashboard)  |
| `pushover` - `disabled` | Disable sending alarms on Pushover. 0 = Alarms will be sent, 1 = Alarms will not be sent. |
| `logging_verbosity` | How much logging output should there be - 1 = Errors only, 2 = General information, 3 = Debugging information. |

### Start syslog-sms

```
sudo systemctl start syslog-sms
sudo systemctl status syslog-sms
```

## Log entries supported

- Running commands with sudo
- Running commands with pkexec
- Logging into terminal with TTY
- Logging into terminal with SSH
- Logging into pfSense web GUI
- Logging into ESXi web GUI
- Logging into OMV web GUI
- Logging into Unifi web GUI
- OpenVPN successful auth
- Wireguard successful auth

## Log entries to be implemented
- Logging into Gnome3 GUI
