# Printer Alarm Clock

A small Python project for scheduled receipt-print routines on a Raspberry Pi with an Epson ESC/POS receipt printer.

It has two main jobs:

- `morning`: 6:30 AM Eastern, Monday-Friday. Prints a good morning receipt with date, weather forecast, and an optional image.
- `nightly-movie`: 7:00 PM Eastern, every day. Prints a movie recommendation with details plus blank spaces for rating and a one-sentence review.

The same rendering code can also generate local HTML previews, so you can design the receipt layout on your computer before printing.

## Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp config.example.json config.json
python -m receipt_alarm_clock.preview --all
```

Open the generated files in `previews/`:

- `previews/morning.html`
- `previews/nightly_movie.html`

You can also print text previews in the terminal:

```bash
python -m receipt_alarm_clock.morning --preview
python -m receipt_alarm_clock.nightly_movie --preview
```

## Configuration

Edit `config.json` after copying it from `config.example.json`.

Important fields:

- `location`: used by Open-Meteo for the morning weather forecast.
- `printer`: Epson ESC/POS connection settings for the Raspberry Pi.
- `morning.image_path`: optional image path to print and show in previews.
- `movie.source_file`: local movie recommendation list.

## Printing

Preview mode is the default. To send output to a configured printer:

```bash
python -m receipt_alarm_clock.morning --print
python -m receipt_alarm_clock.nightly_movie --print
```

For development without printer hardware, use:

```bash
python -m receipt_alarm_clock.morning --preview
python -m receipt_alarm_clock.nightly_movie --preview
```

## Raspberry Pi Cron

Use the IANA timezone name so daylight saving time behaves correctly for Eastern time:

```cron
TZ=America/New_York

30 6 * * 1-5 cd /home/pi/Printer_Alarm_Clock && .venv/bin/python -m receipt_alarm_clock.morning --print >> logs/morning.log 2>&1
0 19 * * * cd /home/pi/Printer_Alarm_Clock && .venv/bin/python -m receipt_alarm_clock.nightly_movie --print >> logs/nightly_movie.log 2>&1
```

Create the log folder on the Pi:

```bash
mkdir -p logs
```

## Printer Notes

This project uses `python-escpos` for real receipt printing. USB is the most common setup for Epson receipt printers on Raspberry Pi.

In `config.json`, set:

```json
"printer": {
  "type": "usb",
  "vendor_id": "0x04b8",
  "product_id": "0x0202"
}
```

The vendor/product IDs vary by model. On the Pi, find them with:

```bash
lsusb
```

## Movie List

Movie recommendations come from `data/movies.json`. Add, remove, or edit entries freely. The nightly script picks a deterministic recommendation based on the current date, which avoids repeats feeling totally random while keeping cron output predictable.
