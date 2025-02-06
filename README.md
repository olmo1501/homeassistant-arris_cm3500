![Version](https://img.shields.io/github/v/release/stickpin/homeassistant-arris_cm3500)
![Downloads](https://img.shields.io/github/downloads/stickpin/homeassistant-arris_cm3500/total)
![CodeStyle](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
[![CodeQL](https://github.com/stickpin/homeassistant-arris_cm3500/actions/workflows/codeql.yml/badge.svg)](https://github.com/stickpin/homeassistant-arris_cm3500/actions/workflows/codeql.yml)


# Home Assistant Integration for Arris CM3500  

## About This Repository  
This integration allows you to monitor the status of your Arris CM3500 cable modem within Home Assistant. It tracks all available channels, including:  
- DOCSIS 3.0 (32 downstream / 8 upstream)  
- DOCSIS 3.1 (2 downstream / 2 upstream)  

You can disable channels that are not in use by your modem.  

### Why Monitor All Channels?  
If you experience connectivity issues due to problems with your CMTS or network infrastructure, you may lose certain downstream or upstream channels. This integration helps you track such behavior, making troubleshooting easier.  

I hope you find this integration useful!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/A0A2S3YXY)

---

## Installation
I recommend installing this integration via [HACS](https://github.com/hacs/integration).  

Since it is not yet part of the official HACS repository, you will need to add it manually:  

1. Navigate to **HACS → Integrations**  
2. Add this repository as a **custom repository**  
3. Search for **Arris CM3500** and install it  
4. Restart Home Assistant  

---

## Features
- **Downstream (DOCSIS 3.0):** 32 QAM channels  
- **Downstream (DOCSIS 3.1):** 2 OFDM channels  
- **Upstream (DOCSIS 3.0):** 8 QAM channels  
- **Upstream (DOCSIS 3.1):** 2 OFDM channels  
