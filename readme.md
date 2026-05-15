# Skatyl Keyboard

## QMK Layouts

The following layout is supported:  
| Layout | Diagram |
| :---: | :---: |
| Split_3x5_3 | ![split_3x5_3](https://i.imgur.com/BHnwCkr.jpg) |

## Base Colemak DH Layout

```text
    ,----------------------------------,                             ,----------------------------------,
    |   Q  |   W  |   F  |   P  |   B  |                             |   J  |   L  |   U  |   Y  |   ;  |
    |------+------+------+------+------|                             |------+------+------+------+------|
    |   A  |   R  |   S  |   T  |   G  |                             |   M  |   N  |   E  |   I  |   O  |
    |------+------+------+------+------|                             |------+------+------+------+------|
    |   Z  |   X  |   C  |   D  |   V  |                             |   K  |   H  |   ,  |   .  |   /  |
    '------+------+------+-------------,                             ,------+------+------+------+------'
                  | GUI  | SPC  | UP   |                             | CTRL | MO(1)|ENTER |
                  '------+------+------'                             '------+------+------'
```

## Note on QMK File Locations

QMK can be confusing regarding where you store your keyboard files. They **must** be placed inside the main cloned QMK repository under either the `keyboards/` or `keyboards/handwired/` directory.

For this specific keyboard, the main files live here:
`$HOME\qmk_firmware\keyboards\skatyl\`

> [!WARNING]
> Please ignore the following directories as they are just backups or outdated:
> - `$HOME\qmk_firmware\keyboards\handwired\skatyl`
> - `$HOME\qmk_firmware\keyboards\scatyl`

## Entering Bootloader Mode

Before flashing either half, put it into bootloader mode so it appears as a USB drive called `RPI-RP2`.

**Method 1 — Unplug method (easiest for bare boards):**
1. Unplug the USB cable.
2. Hold **BOOT**, plug USB back in, release BOOT.

**Method 2 — Two-button method (already plugged in):**
1. Hold **BOOT**, press and release **RESET**, then release BOOT.

---

## Building and Flashing

### Option A — Compile only

Produces a `skatyl_no_numrow.uf2` file in the `qmk_firmware` directory. Flash it manually afterward.

Open QMK MSYS, `cd ~/qmk_firmware`, then run:

```bash
qmk compile -kb skatyl -km no_numrow
```

---

### Option B — Compile, then flash

Open QMK MSYS, `cd ~/qmk_firmware`, compile first, then put each half into bootloader mode and run:

```bash
qmk compile -kb skatyl -km no_numrow
qmk flash -kb skatyl -km no_numrow -bl uf2-split-left   # flash left half
qmk flash -kb skatyl -km no_numrow -bl uf2-split-right  # flash right half
```

---

### Option C — Compile and flash in one step

Compiles the firmware and immediately waits for you to put a half into bootloader mode. Run once per half.

Open QMK MSYS, `cd ~/qmk_firmware`, then run:

```bash
qmk flash -kb skatyl -km no_numrow -bl uf2-split-left   # put left half into bootloader when prompted
qmk flash -kb skatyl -km no_numrow -bl uf2-split-right  # put right half into bootloader when prompted
```

---

### Option D — Flash a downloaded .uf2 (no build tools needed)

Download `skatyl_no_numrow.uf2` from the [Releases page](https://github.com/siddAhmed/skatyl/releases/latest). Put one half into bootloader mode — it appears as `RPI-RP2`. Drag `skatyl_no_numrow.uf2` onto it, wait for it to reboot, then repeat for the other half. Both sides use the same file.
