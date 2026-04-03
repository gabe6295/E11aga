"""
Communication module for the CapeSym MCA radiation sensor.

Requires:
    sudo apt install libusb-1.0-0-dev
    pip install pyusb

For non-root USB access on Raspberry Pi, create /etc/udev/rules.d/50-capemca.rules:
    SUBSYSTEMS=="usb",ATTRS{idVendor}=="4701",ATTRS{idProduct}=="0290",GROUP="users",MODE="0666"
Then reboot or run: sudo udevadm control --reload-rules && sudo udevadm trigger
"""

import struct
import usb.core
import usb.util
import argparse
import time
import csv
from datetime import datetime

# Dummy constants and classes for debugging; replace with actual implementations
SPECTRUM_CHANNELS = 1025  # Example: 1024 channels + 1 header

class Status:
    def __init__(self):
        self.cps = 100
        self.total_count = 10000
        self.total_intervals = 1

def find_all_mcas():
    # Replace with actual device discovery
    return [1]

class CapeMCA:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def read_status(self):
        return Status()
    def read_spectrum(self):
        # Return a dummy spectrum: [header, ch1, ch2, ..., chN]
        return [0] + [0]*SPECTRUM_CHANNELS


parser = argparse.ArgumentParser()
parser.add_argument("-t", "--time", type=int, default=60, help="Total run time (sec)")
parser.add_argument("-i", "--interval", type=int, default=5, help="Logging interval (sec)")
parser.add_argument("-o", "--output", type=str, default="mca_log.csv", help="Output filename")
args, _ = parser.parse_known_args()


if __name__ == '__main__':
    import sys
    import time
    import numpy as np
    import matplotlib.pyplot as plt

    devices = find_all_mcas()
    print(f"Found {len(devices)} MCA device(s)")

    output_file = sys.argv[3] if len(sys.argv) > 3 else "mca_data.csv"

    if not devices:
        sys.exit(1)

    duration = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
    window = float(sys.argv[2]) if len(sys.argv) > 2 else 15.0


    f = open(output_file, 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Elapsed_Sec", "CPS", "Total_Counts"])

    spectra = []
    read_times = []

    with CapeMCA() as mca:
        try:
            start = time.time()
            reads = 0
            next_read = start

            while time.time() - start < duration:
                # Wait until the next window boundary
                now = time.time()
                if now < next_read:
                    time.sleep(next_read - now)

                read_start = time.time()
                status = mca.read_status()
                spectrum = mca.read_spectrum()
                read_end = time.time()

                # Schedule next read from when this one started
                next_read = read_start + window

                spec_data = spectrum[1:]
                spec_total = sum(spec_data)
                nonzero = sum(1 for ch in spec_data if ch > 0)
                elapsed = read_start - start

                # Task B: Save current interval counts and timestamp
                ts = datetime.now().strftime("%H:%M:%S")
                writer.writerow([ts, f"{elapsed:.1f}", status.cps, status.total_count])
                f.flush()
                
                print(f"[{elapsed:6.1f}s] read {reads+1} "
                      f"(took {read_end - read_start:.2f}s): "
                      f"{status.cps} cps, "
                      f"totalCount={status.total_count:g}, "
                      f"intervals={status.total_intervals}")
                print(f"         spectrum: ch0={spectrum[0]}, specSum={spec_total}, "
                      f"nonzeroCh={nonzero}")

                active = [(ch, spectrum[ch]) for ch in range(1, SPECTRUM_CHANNELS)
                          if spectrum[ch] > 0]
                print(f"         channels: {active}")

                spectra.append(spec_data)
                read_times.append(elapsed)
                reads += 1

            print(f"\nCompleted {reads} reads in {time.time() - start:.2f}s "
                  f"(window={window}s)")

        except Exception as e:
            print(f"\nError after {reads} reads: {e}")

    print("Device closed, exiting.")

    if spectra:
        waterfall = np.array(spectra)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Top: waterfall heatmap — channels vs read number
        im = ax1.imshow(waterfall, aspect='auto', origin='lower',
                        extent=[1, SPECTRUM_CHANNELS - 1, 0.5, len(spectra) + 0.5],
                        interpolation='nearest', cmap='hot')
        ax1.set_xlabel("Channel")
        ax1.set_ylabel("Read #")
        ax1.set_title(f"Spectrum waterfall ({window}s window)")
        # Label y-axis ticks with timestamps
        yticks = list(range(1, len(spectra) + 1))
        ylabels = [f"{reads} ({t:.0f}s)" for reads, t in zip(yticks, read_times)]
        ax1.set_yticks(yticks)
        ax1.set_yticklabels(ylabels, fontsize=7)
        fig.colorbar(im, ax=ax1, label="Counts")

        # Bottom: summed spectrum (log scale)
        summed = waterfall.sum(axis=0)
        ax2.plot(range(1, SPECTRUM_CHANNELS), summed, 'k-', linewidth=0.8)
        ax2.set_yscale('log')
        ax2.set_xlabel("Channel")
        ax2.set_ylabel("Counts (summed)")
        ax2.set_title(f"Summed spectrum ({len(spectra)} reads, {window}s windows)")

        plt.tight_layout()
        plt.savefig("spectra.png", dpi=150)
        print("Plot saved to spectra.png")
        plt.show()
