# syslog-sms
Monitor syslog and text when something interesting happens

## Dependencies

- python3
- twilio python sdk
- systemd

## Installation

### Install syslog-sms and Dependencies

#### Debian/Ubuntu/apt Based Distributions
```
sudo apt install python3 python3-pip git
sudo pip3 install twilio
sudo git clone https://github.com/dhminch/syslog-sms.git /opt
sudo cp /opt/syslog-sms/syslog-sms.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable syslog-sms
```

#### RHEL/CentOS/yum Based Distributions:

```
sudo yum install python3 python3-pip git
sudo pip3 install twilio
sudo git clone https://github.com/dhminch/syslog-sms.git /opt
sudo cp /opt/syslog-sms/syslog-sms.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable syslog-sms
```

### Configure syslog-sms

```
cp /opt/syslog-sms/config.json.template /opt/syslog-sms/config.json
```

Edit config.json to suit your needs. The configurable fields are:

| Field | Description |
| --- | --- |
| `logs` | Comma separated list of files to monitor. Each file should be in quotes. |
| `cellphone` | The cell phone number to text alerts to. Should be your country code (e.g., +1) plus the rest of your normal number. |
| `monitor_frequency` | How often, in seconds, the log files should be checked for updates. 30-60 seconds is a good value. |
| `limits` - `host_cooldown` | How long, in seconds, to wait to send another alarm for a particular host (to avoid spamming you). |
| `limits` - `max_per_hour` | Max number of alarms to send in an hour (to avoid spamming you and keep costs down). |
| `limits` - `max_per_day` | Max number of alarms to send in a day (to avoid spamming you and keep costs down). |
| `twilio` - `account_sid` | Your Twilio Account SID (on your Twilio Dashboard) |
| `twilio` - `auth_token` | Your Twilio Auth Token (on your Twilio Dashboard)  |
| `twilio` - `messagingservice_sid` | Your Twilio Messasing Service SID (under the Messaging Service you created). |
| `twilio` - `disabled` | Disable sending alarms on Twilio. 0 = Alarms will be sent, 1 = Alarms will not be sent. |
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

## Log entries to be implemented

- OpenVPN successful auth
- Logging into Gnome3 GUI
- Logging into Unifi web GUI
- Logging into OMV web GUI