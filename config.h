// Cosmos documentation config
#pragma once
#define SERIAL_DEBUG

// #include_next <halconf.h>
// #define PAL_USE_CALLBACKS TRUE

#define EE_HANDS // Store which side I am in EEPROM
// #define SPLIT_USB_DETECT // This should be enabled by default.

// #define SOFT_SERIAL_PIN GP0  // The GPIO pin that is used for split communication.
// #define SERIAL_USART_TX_PIN GP13     // The GPIO pin that is used split communication.

// #define DIODE_DIRECTION ROW2COL
#define MATRIX_ROWS 10  // 5 rows per half (including number row)
#define MATRIX_COLS 10 // 5 columns per half

/* Keyboard matrix assignments */
// #define MATRIX_ROW_PINS {GP15, GP29, GP28, GP27, GP26}
#define MATRIX_ROW_PINS {GP15, GP29, GP28, GP14, GP26}
#define MATRIX_COL_PINS {GP2, GP3, GP4, GP5, GP6}

/* Reset */
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET_LED GP17
// This LED blinks when entering bootloader

// Ben Vallack's config
#undef TAPPING_TERM
#define TAPPING_TERM 240
#define RETRO_TAPPING

#undef MOUSEKEY_DELAY
#define MOUSEKEY_DELAY 5
#undef MOUSEKEY_INTERVAL
#define MOUSEKEY_INTERVAL 16
#undef MOUSEKEY_MOVE_DELTA
#define MOUSEKEY_MOVE_DELTA 1
#undef MOUSEKEY_INITIAL_SPEED
#define MOUSEKEY_INITIAL_SPEED 1
#undef MOUSEKEY_DECELERATED_SPEED
#define MOUSEKEY_DECELERATED_SPEED 12
#undef MOUSEKEY_MAX_SPEED
#define MOUSEKEY_MAX_SPEED 22
#define USB_SUSPEND_WAKEUP_DELAY 0
#undef MOUSEKEY_WHEEL_INTERVAL
#define MOUSEKEY_WHEEL_INTERVAL 83

#undef MOUSEKEY_WHEEL_INTERVAL
#define MOUSEKEY_WHEEL_INTERVAL 83

#undef MOUSEKEY_WHEEL_MAX_SPEED
#define MOUSEKEY_WHEEL_MAX_SPEED 3
