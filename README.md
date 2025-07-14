# MEXC Spot Pump Trading Bot

This bot scans the top 100 coins by volume on MEXC spot market. It detects fast-pumping tokens and enters spot trades.

## Setup

1. Clone the repository.
2. Add `.env` file using `.env.example` as reference.
3. Deploy on Railway or similar cloud platform.

## Features

- Scans top 100 MEXC tokens by volume
- Buys when 3%+ gain detected in last 5 minutes
- Fixed $25 per trade
- Telegram alerts and hourly reports
