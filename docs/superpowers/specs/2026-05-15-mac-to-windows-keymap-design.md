# Mac → Windows Keymap Conversion — Design Spec
**Date:** 2026-05-15  
**Keymap:** `keymaps/no_numrow/keymap.c`  
**Keyboard:** Skatyl 3x5 split, Colemak DH, RP2040 Zero

---

## Background

The `no_numrow` keymap was originally designed for a **UK Mac** layout. Evidence:
- Home row mods use `LGUI`/`RGUI` (= Command on Mac)
- `LALT(KC_3)` = `#` on UK Mac's Option+3
- `LALT(KC_RBRC/LBRC)` = Mac curly quotes via Option key
- Layer 3 shortcuts use `LGUI(...)` for browser back/forward, app switcher, etc.

The user is on **Windows 10/11 with a US keyboard layout**. CTRL is the primary text-editing modifier; the Win key (`LGUI`) is used for OS-level shortcuts (Win+Tab, Win+D, etc.).

---

## Decisions Made

| Decision | Choice | Reason |
|---|---|---|
| Home row GUI mods (`T`/`N`) | **Keep as GUI** | CTRL is already on the right thumb (`OSM(MOD_RCTL)`); GUI home row mods are useful for Win+shortcuts |
| Curly quotes | **Replace with straight quotes / repurpose** | Mac Option+bracket combos produce nothing useful on Windows |
| Right-arrow hold | **`KC_END` (end of line)** | Preserves Mac intent: left-hold = word-jump, right-hold = end of line |
| Rupee symbol | **WinCompose + `register_unicode(0x20B9)`** | No native Windows way to type arbitrary Unicode from firmware without extra software |
| Force Quit → | **`LALT(KC_F4)`** | Same intent as Mac Force Quit — quit the current app |

---

## Section 1: Layer 1 Changes (Symbols)

### Key map changes

| Position | Key in layout | Was (Mac) | Becomes (Windows) |
|---|---|---|---|
| R1C3 | Direct key | `MT(KC_PSCR, LSFT(KC_3))` — invalid MT | `KC_PSCR` (full-screen Print Screen) |
| R1C4 | `DANCE_31` hold | `LCTL(LGUI(LSFT(KC_4)))` Mac screenshot | `LGUI(LSFT(KC_S))` Win+Shift+S Snipping Tool |
| R2C3 | Direct key | `LALT(KC_RBRC)` curly `'` | `KC_LABK` = `<` |
| R2C4 | Direct key | `LALT(LSFT(KC_RBRC))` curly `'` | `KC_RABK` = `>` |
| R2C5 | `DANCE_32` hold | `LGUI(KC_QUOTE)` Cmd+' | `LGUI(KC_PERIOD)` Win+. emoji picker |
| R3C2 | `DANCE_33` tap/hold | `LALT(KC_3)` = `£` / `LALT(LSFT(KC_2))` = `€` | tap = `KC_DLR` (`$`) / hold = `register_unicode(0x20B9)` (`₹`) |
| R3C3 | Direct key | `LALT(KC_LBRC)` curly `"` | `KC_COLN` = `:` |
| R3C4 | Direct key | `LALT(LSFT(KC_LBRC))` curly `"` | `KC_QUES` = `?` |

### Notes on R1C3 (`MT(KC_PSCR, LSFT(KC_3))`)

`MT(mod, kc)` requires `mod` to be a modifier bitmask (`MOD_LSFT`, `MOD_LCTL`, etc.). `KC_PSCR` is a keycode, not a modifier — this key was silently producing random modifier combinations on hold. Replaced with plain `KC_PSCR`. Full-screen screenshot and area screenshot (Win+Shift+S) are now both accessible from Layer 1.

### Resulting Layer 1 left-hand symbol coverage

```
Row 1:  ESC   @    PSCR   $/%  %
Row 2:  TAB   =    <      >    '/" (DANCE_32)
Row 3:  ~     $/₹  :      ?    "
```

Missing-from-L1 symbols now added: `<`, `>`, `:`, `?`, `$` (ergonomic slot), `₹`.

### Rupee symbol implementation

Requires `UNICODE_ENABLE = yes` (added to `keymaps/no_numrow/rules.mk`).  
Requires **WinCompose** installed and running on Windows (free, open-source, system tray app).  
Unicode mode set in `keyboard_post_init_user`: `set_unicode_input_mode(UNICODE_MODE_WINCOMPOSE)`.

DANCE_33 `finished` SINGLE_HOLD case calls `register_unicode(0x20B9)`.  
DANCE_33 `reset`: SINGLE_TAP/DOUBLE_TAP/DOUBLE_SINGLE_TAP unregister `KC_DLR`; SINGLE_HOLD is a no-op (Unicode send is self-contained, no unregister needed).

---

## Section 2: Layer 3 Changes (Navigation / Shortcuts)

### Key map changes

| Key | Was (Mac) | Becomes (Windows) |
|---|---|---|
| R1C1 `LGUI(KC_LBRC)` | Cmd+[ browser back | `KC_WBAK` dedicated HID browser-back |
| R1C5 `LGUI(KC_RBRC)` | Cmd+] browser forward | `KC_WFWD` dedicated HID browser-forward |
| `DANCE_54` hold | `LALT(LGUI(KC_ESCAPE))` Force Quit | `LALT(KC_F4)` close/quit window |
| `DANCE_56` hold | `LGUI(KC_TAB)` Cmd+Tab app switcher | `LALT(KC_TAB)` Alt+Tab |
| `DANCE_58` hold | `LGUI(KC_GRAVE)` next window same app | `LGUI(KC_TAB)` Win+Tab Task View |
| `DANCE_60` hold | `LALT(KC_LEFT)` Option+Left word-jump | `LCTL(KC_LEFT)` Ctrl+Left word-jump |
| `DANCE_63` hold | `LGUI(KC_RIGHT)` Cmd+Right end-of-line | `KC_END` End key |

### Bug fixes

Two dances had mismatched `finished`/`reset` key pairs, causing the hold key to remain "stuck" after release:

| Dance | `finished` registered | `reset` unregistered (BUG) | Fixed `reset` |
|---|---|---|---|
| `DANCE_60` SINGLE_HOLD | `LALT(KC_LEFT)` | `LGUI(KC_LEFT)` | `LCTL(KC_LEFT)` |
| `DANCE_63` SINGLE_HOLD | `LGUI(KC_RIGHT)` | `LALT(KC_RIGHT)` | `KC_END` |

---

## Section 3: Code Cleanup

| Item | Action |
|---|---|
| `keyboard_post_init_user` debug flags | Rewrite: remove `debug_enable`/`debug_matrix`, add `set_unicode_input_mode(UNICODE_MODE_WINCOMPOSE)` |
| `DANCE_15` | Remove — defined, registered in `tap_dance_actions`, unreachable from any layer |
| `DANCE_57` | Remove — same |
| `DANCE_59` | Remove — same |
| `DANCE_33` functions | Rewrite for `$`/`₹` behavior |
| `keymaps/no_numrow/rules.mk` | Create with `UNICODE_ENABLE = yes` |

---

## Files Changed

| File | Change type |
|---|---|
| `keymaps/no_numrow/keymap.c` | Modify — all key remaps, dance rewrites, dead code removal |
| `keymaps/no_numrow/rules.mk` | Create — `UNICODE_ENABLE = yes` |

---

## Out of Scope

- Layers 0, 2: no changes
- Other keymaps (`default`, `numrow`): not touched
- `config.h`, root `rules.mk`: not touched
- Home row mod keys (`T`/`N` = GUI): kept as-is by design decision
