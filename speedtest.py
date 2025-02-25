#!/usr/bin/python
import datetime
import os
import re
import subprocess
import logging
import sys
sys.path.insert(1, "./lib")  # Add library path

import epd2in13b_V4  # Import display driver for black, white, and red display
from PIL import Image, ImageDraw, ImageFont

# Get current date and time
now = datetime.datetime.now()

# Run speed test and capture output
response = subprocess.Popen('speedtest-cli --secure --simple', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')

# Extract values using regex
ping = re.findall(r'Ping:\s(.*?)\s', response, re.MULTILINE)
download = re.findall(r'Download:\s(.*?)\s', response, re.MULTILINE)
upload = re.findall(r'Upload:\s(.*?)\s', response, re.MULTILINE)

# Convert values to float and round to 1 decimal place
ping = round(float(ping[0]), 1) if ping else 0.0
download = round(float(download[0]), 1) if download else 0.0
upload = round(float(upload[0]), 1) if upload else 0.0

try:
    # Initialize the e-Paper display
    epd = epd2in13b_V4.EPD()
    epd.init()
    epd.Clear()

    # Create black and red images
    imageblack = Image.new('1', (epd.height, epd.width), 255)  # White background
    imagered = Image.new('1', (epd.height, epd.width), 255)  # White background

    draw_black = ImageDraw.Draw(imageblack)
    draw_red = ImageDraw.Draw(imagered)

    # Load fonts
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if not os.path.exists(font_path):
        font_path = "./font/Font.ttc"

    title_font = ImageFont.truetype(font_path, 22)  # Title font
    font = ImageFont.truetype(font_path, 16)  # Main text font
    font_small = ImageFont.truetype(font_path, 12)  # Small text font

    # Get screen width
    screen_width = epd.height

    # Center "SPEEDTEST" text
    speedtest_text = "SPEEDTEST"
    speedtest_width = draw_black.textbbox((0, 0), speedtest_text, font=title_font)[2]
    speedtest_x = (screen_width - speedtest_width) // 2
    draw_black.text((speedtest_x, 5), speedtest_text, font=title_font, fill=0)

    # Center the date and time
    datetime_text = now.strftime("%d-%m-%Y %H:%M")  # Full year format
    datetime_width = draw_black.textbbox((0, 0), datetime_text, font=font_small)[2]
    datetime_x = (screen_width - datetime_width) // 2
    draw_black.text((datetime_x, 30), datetime_text, font=font_small, fill=0)

    # Define column widths (Ping is smaller, Download is wider)
    ping_width = 60
    download_width = 100
    upload_width = 80
    margin = 2

    # Calculate column positions
    x_ping = margin
    x_download = x_ping + ping_width + margin
    x_upload = x_download + download_width + margin

    row1_y = 65  # Headers
    row2_y = 90  # Values
    row3_y = 105  # Units
    row4_y = 140  # Bottom border

    # Draw table lines
    table_width = x_upload + upload_width  # Total table width
    draw_black.line([(margin, row1_y - 5), (table_width, row1_y - 5)], fill=0, width=2)  # Top line
    #draw_black.line([(margin, row4_y + 10), (table_width, row4_y + 10)], fill=0, width=2)  # Bottom line
    draw_black.line([(x_download - margin + 5, row1_y - 5), (x_download - margin + 5, row4_y + 10)], fill=0, width=2)  # Vertical line 1
    draw_black.line([(x_upload - margin + 5, row1_y - 5), (x_upload - margin + 5, row4_y + 10)], fill=0, width=2)  # Vertical line 2

    # Draw table headers (black)
    draw_black.text((x_ping + (ping_width // 4) - 3, row1_y), "Ping", font=font, fill=0)
    draw_black.text((x_download + (download_width // 8), row1_y), "Download", font=font, fill=0)
    draw_black.text((x_upload + (upload_width // 6), row1_y), "Upload", font=font, fill=0)

    # Center values under headers (red)
    ping_text = f"({ping})"
    download_text = f"({download})"
    upload_text = f"({upload})"

    # Calculate text width for centering
    ping_w = draw_red.textbbox((0, 0), ping_text, font=font)[2]
    download_w = draw_red.textbbox((0, 0), download_text, font=font)[2]
    upload_w = draw_red.textbbox((0, 0), upload_text, font=font)[2]

    draw_red.text((x_ping + (ping_width - ping_w) // 2, row2_y), ping_text, font=font, fill=0)
    draw_red.text((x_download + (download_width - download_w) // 2, row2_y), download_text, font=font, fill=0)
    draw_red.text((x_upload + (upload_width - upload_w) // 2, row2_y), upload_text, font=font, fill=0)

    # Center units below values (red)
    draw_red.text((x_ping + (ping_width // 3), row3_y), "ms", font=font_small, fill=0)
    draw_red.text((x_download + (download_width // 3), row3_y), "Mbps", font=font_small, fill=0)
    draw_red.text((x_upload + (upload_width // 3), row3_y), "Mbps", font=font_small, fill=0)

    # Rotate images (based on display orientation)
    imageblack = imageblack.rotate(180)
    imagered = imagered.rotate(180)

    # Display image on e-Ink screen
    epd.display(epd.getbuffer(imageblack), epd.getbuffer(imagered))

    epd.sleep()
    epd2in13b_V4.epdconfig.module_exit(cleanup=True)

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in13b_V4.epdconfig.module_exit()
    exit()

