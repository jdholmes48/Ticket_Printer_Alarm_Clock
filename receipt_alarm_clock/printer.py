from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .renderer import Receipt


class PrinterUnavailable(RuntimeError):
    pass


def print_receipt(receipt: Receipt, config: Dict[str, Any]) -> None:
    printer = _make_printer(config["printer"])

    if receipt.image_path and Path(receipt.image_path).exists():
        printer.image(str(receipt.image_path))
        printer.text("\n")

    printer.text(receipt.to_text())
    printer.cut()


def _make_printer(config: Dict[str, Any]):
    try:
        from escpos.printer import Network, Serial, Usb
    except ImportError as exc:
        raise PrinterUnavailable(
            "python-escpos is not installed. Run `pip install -r requirements.txt`."
        ) from exc

    printer_type = config.get("type", "usb").lower()
    profile = config.get("profile")

    if printer_type == "usb":
        vendor_id = int(str(config["vendor_id"]), 16)
        product_id = int(str(config["product_id"]), 16)
        return Usb(vendor_id, product_id, profile=profile)

    if printer_type == "network":
        return Network(config["host"], port=int(config.get("port", 9100)), profile=profile)

    if printer_type == "serial":
        return Serial(devfile=config.get("device", "/dev/ttyUSB0"), baudrate=int(config.get("baudrate", 9600)), profile=profile)

    raise PrinterUnavailable(f"Unsupported printer type: {printer_type}")
