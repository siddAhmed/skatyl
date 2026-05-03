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

## How to Compile

1. Open QMK MSYS (either directly or in your Windows Terminal profile).
2. Change directory to the root of your QMK firmware:
   ```bash
   cd ~/qmk_firmware
   ```
3. Run one of the following commands depending on the keymap you want to build:
   ```bash
   qmk compile -kb skatyl -km numrow
   # or
   qmk compile -kb skatyl -km no_numrow
   # or
   qmk compile -kb skatyl -km default
   ```

## How to Flash

Before flashing, you must put the RP2040 Zero into bootloader mode (BOOTSEL mode) so it shows up as a USB drive (`RPI-RP2`) on your computer.

### Entering Bootloader Mode

You can use either of the following methods using the tiny buttons on the board:

**Method 1: The Plug-in Method (Easiest for bare boards)**
1. Unplug the USB cable from the RP2040 Zero.
2. Press and **hold down the BOOT button**.
3. While continuing to hold the BOOT button, plug the USB cable back into your computer.
4. Release the BOOT button.

**Method 2: The Two-Button Method (If already plugged in)**
1. Press and **hold down the BOOT button**.
2. While holding BOOT, quickly press and release the **RESET** button.
3. Release the **BOOT** button.

### Flashing Commands

Once in bootloader mode, run the following commands:

```bash
qmk flash -kb skatyl -km no_numrow -bl uf2-split-right
# and
qmk flash -kb skatyl -km no_numrow -bl uf2-split-left
```

> **Flashing directly**  
> You can directly run the flash command as it compiles the firmware first anyways.
