# Mac → Windows Keymap Conversion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert `keymaps/no_numrow/keymap.c` from a UK-Mac layout to Windows, fixing broken shortcuts, removing Mac-specific key combos, adding missing symbols, and cleaning up dead code.

**Architecture:** All changes are isolated to two files: the existing `keymap.c` (key remaps, tap-dance rewrites, dead code removal) and a new `rules.mk` (enables Unicode feature). No new layers, no structural changes to the layout. Compile after each task to catch errors early — QMK has no unit test suite for custom keymaps; a successful compile is the verification step.

**Tech Stack:** QMK Firmware (C), RP2040, tap-dance feature, Unicode feature (WinCompose mode)

---

## Pre-flight

> Run all compile commands from **QMK MSYS** with working directory `~/qmk_firmware`.  
> The keyboard files at `C:/dev/skatyl` must be the active files under `~/qmk_firmware/keyboards/skatyl/`.

Baseline compile — confirm the keymap builds before any changes:
```bash
qmk compile -kb skatyl -km no_numrow
```
Expected: build succeeds, produces `skatyl_no_numrow.uf2`.

---

## File Map

| File | Change |
|---|---|
| `keymaps/no_numrow/rules.mk` | **Create** — enable Unicode feature |
| `keymaps/no_numrow/keymap.c` | **Modify** — all changes below |

---

## Task 1: Infrastructure — Unicode support and init rewrite

**Files:**
- Create: `keymaps/no_numrow/rules.mk`
- Modify: `keymaps/no_numrow/keymap.c` (top of file)

- [ ] **Step 1: Create `keymaps/no_numrow/rules.mk`**

Create the file with this exact content:
```makefile
UNICODE_ENABLE = yes
```

- [ ] **Step 2: Rewrite `keyboard_post_init_user` in `keymap.c`**

Replace:
```c
void keyboard_post_init_user(void) {
  debug_enable=true;
  debug_matrix=true;
}
```
With:
```c
void keyboard_post_init_user(void) {
    set_unicode_input_mode(UNICODE_MODE_WINCOMPOSE);
}
```

- [ ] **Step 3: Compile**
```bash
qmk compile -kb skatyl -km no_numrow
```
Expected: build succeeds. If you see `'UNICODE_MODE_WINCOMPOSE' undeclared`, confirm `rules.mk` was saved in the right location.

- [ ] **Step 4: Commit**
```bash
git add keymaps/no_numrow/rules.mk keymaps/no_numrow/keymap.c
git commit -m "feat: enable Unicode (WinCompose) and remove debug flags"
```

---

## Task 2: Remove dead tap-dance code (DANCE_15, DANCE_57, DANCE_59)

These three dances are registered in `tap_dance_actions` but unreachable from any layer — dead code that wastes flash.

**Files:**
- Modify: `keymaps/no_numrow/keymap.c`

- [ ] **Step 1: Remove `DANCE_15`, `DANCE_57`, `DANCE_59` from the enum**

Find and edit the enum at the top of `keymap.c`. Remove three entries:
```c
// REMOVE these three lines from the enum:
  DANCE_15,
  DANCE_57,
  DANCE_59,
```
The enum should go from this:
```c
enum tap_dance_codes {
  DANCE_1,
  DANCE_2,
  DANCE_3,
  DANCE_15,    // <- remove
  DANCE_31,
  DANCE_32,
  DANCE_33,
  DANCE_54,
  DANCE_55,
  DANCE_56,
  DANCE_57,    // <- remove
  DANCE_58,
  DANCE_59,    // <- remove
  DANCE_60,
  DANCE_63,
  BKSL_HME,
  PIPE_END,
};
```
To this:
```c
enum tap_dance_codes {
  DANCE_1,
  DANCE_2,
  DANCE_3,
  DANCE_31,
  DANCE_32,
  DANCE_33,
  DANCE_54,
  DANCE_55,
  DANCE_56,
  DANCE_58,
  DANCE_60,
  DANCE_63,
  BKSL_HME,
  PIPE_END,
};
```

- [ ] **Step 2: Remove the DANCE_15 forward declarations and function bodies**

Delete this entire block (forward declarations + 4 function bodies):
```c
void on_dance_15(tap_dance_state_t *state, void *user_data);
uint8_t dance_15_dance_step(tap_dance_state_t *state);
void dance_15_finished(tap_dance_state_t *state, void *user_data);
void dance_15_reset(tap_dance_state_t *state, void *user_data);

void on_dance_15(tap_dance_state_t *state, void *user_data) {
    if(state->count == 3) {
        tap_code16(KC_SPACE);
        tap_code16(KC_SPACE);
        tap_code16(KC_SPACE);
    }
    if(state->count > 3) {
        tap_code16(KC_SPACE);
    }
}

uint8_t dance_15_dance_step(tap_dance_state_t *state) {
    if (state->count == 1) {
        if (state->interrupted || !state->pressed) return SINGLE_TAP;
        else return SINGLE_HOLD;
    } else if (state->count == 2) {
        if (state->interrupted) return DOUBLE_SINGLE_TAP;
        else if (state->pressed) return DOUBLE_HOLD;
        else return DOUBLE_TAP;
    }
    return MORE_TAPS;
}
void dance_15_finished(tap_dance_state_t *state, void *user_data) {
    dance_state.step = dance_15_dance_step(state);
    switch (dance_state.step) {
        case SINGLE_TAP: register_code16(KC_SPACE); break;
        case SINGLE_HOLD: register_code16(KC_UNDS); break;
        case DOUBLE_TAP: register_code16(KC_SPACE); register_code16(KC_SPACE); break;
        case DOUBLE_SINGLE_TAP: tap_code16(KC_SPACE); register_code16(KC_SPACE);
    }
}

void dance_15_reset(tap_dance_state_t *state, void *user_data) {
    wait_ms(10);
    switch (dance_state.step) {
        case SINGLE_TAP: unregister_code16(KC_SPACE); break;
        case SINGLE_HOLD: unregister_code16(KC_UNDS); break;
        case DOUBLE_TAP: unregister_code16(KC_SPACE); break;
        case DOUBLE_SINGLE_TAP: unregister_code16(KC_SPACE); break;
    }
    dance_state.step = 0;
}
```

- [ ] **Step 3: Remove the DANCE_57 forward declarations and function bodies**

Delete this entire block:
```c
void on_dance_57(tap_dance_state_t *state, void *user_data);
uint8_t dance_57_dance_step(tap_dance_state_t *state);
void dance_57_finished(tap_dance_state_t *state, void *user_data);
void dance_57_reset(tap_dance_state_t *state, void *user_data);

void on_dance_57(tap_dance_state_t *state, void *user_data) {
    if(state->count == 3) {
        tap_code16(KC_DELETE);
        tap_code16(KC_DELETE);
        tap_code16(KC_DELETE);
    }
    if(state->count > 3) {
        tap_code16(KC_DELETE);
    }
}

uint8_t dance_57_dance_step(tap_dance_state_t *state) {
    if (state->count == 1) {
        if (state->interrupted || !state->pressed) return SINGLE_TAP;
        else return SINGLE_HOLD;
    } else if (state->count == 2) {
        if (state->interrupted) return DOUBLE_SINGLE_TAP;
        else if (state->pressed) return DOUBLE_HOLD;
        else return DOUBLE_TAP;
    }
    return MORE_TAPS;
}
void dance_57_finished(tap_dance_state_t *state, void *user_data) {
    dance_state.step = dance_57_dance_step(state);
    switch (dance_state.step) {
        case SINGLE_TAP: register_code16(KC_DELETE); break;
        case SINGLE_HOLD: register_code16(LCTL(KC_K)); break;
        case DOUBLE_TAP: register_code16(KC_DELETE); register_code16(KC_DELETE); break;
        case DOUBLE_SINGLE_TAP: tap_code16(KC_DELETE); register_code16(KC_DELETE);
    }
}

void dance_57_reset(tap_dance_state_t *state, void *user_data) {
    wait_ms(10);
    switch (dance_state.step) {
        case SINGLE_TAP: unregister_code16(KC_DELETE); break;
        case SINGLE_HOLD: unregister_code16(LCTL(KC_K)); break;
        case DOUBLE_TAP: unregister_code16(KC_DELETE); break;
        case DOUBLE_SINGLE_TAP: unregister_code16(KC_DELETE); break;
    }
    dance_state.step = 0;
}
```

- [ ] **Step 4: Remove the DANCE_59 forward declarations and function bodies**

Delete this entire block:
```c
void on_dance_59(tap_dance_state_t *state, void *user_data);
uint8_t dance_59_dance_step(tap_dance_state_t *state);
void dance_59_finished(tap_dance_state_t *state, void *user_data);
void dance_59_reset(tap_dance_state_t *state, void *user_data);

void on_dance_59(tap_dance_state_t *state, void *user_data) {
    if(state->count == 3) {
        tap_code16(KC_SPACE);
        tap_code16(KC_SPACE);
        tap_code16(KC_SPACE);
    }
    if(state->count > 3) {
        tap_code16(KC_SPACE);
    }
}

uint8_t dance_59_dance_step(tap_dance_state_t *state) {
    if (state->count == 1) {
        if (state->interrupted || !state->pressed) return SINGLE_TAP;
        else return SINGLE_HOLD;
    } else if (state->count == 2) {
        if (state->interrupted) return DOUBLE_SINGLE_TAP;
        else if (state->pressed) return DOUBLE_HOLD;
        else return DOUBLE_TAP;
    }
    return MORE_TAPS;
}
void dance_59_finished(tap_dance_state_t *state, void *user_data) {
    dance_state.step = dance_59_dance_step(state);
    switch (dance_state.step) {
        case SINGLE_TAP: register_code16(KC_SPACE); break;
        case SINGLE_HOLD: register_code16(LGUI(KC_O)); break;
        case DOUBLE_TAP: register_code16(KC_SPACE); register_code16(KC_SPACE); break;
        case DOUBLE_SINGLE_TAP: tap_code16(KC_SPACE); register_code16(KC_SPACE);
    }
}

void dance_59_reset(tap_dance_state_t *state, void *user_data) {
    wait_ms(10);
    switch (dance_state.step) {
        case SINGLE_TAP: unregister_code16(KC_SPACE); break;
        case SINGLE_HOLD: unregister_code16(LGUI(KC_O)); break;
        case DOUBLE_TAP: unregister_code16(KC_SPACE); break;
        case DOUBLE_SINGLE_TAP: unregister_code16(KC_SPACE); break;
    }
    dance_state.step = 0;
}
```

- [ ] **Step 5: Remove the three entries from `tap_dance_actions`**

In the `tap_dance_actions[]` array at the bottom of the file, delete these three lines:
```c
        [DANCE_15] = ACTION_TAP_DANCE_FN_ADVANCED(on_dance_15, dance_15_finished, dance_15_reset),
        [DANCE_57] = ACTION_TAP_DANCE_FN_ADVANCED(on_dance_57, dance_57_finished, dance_57_reset),
        [DANCE_59] = ACTION_TAP_DANCE_FN_ADVANCED(on_dance_59, dance_59_finished, dance_59_reset),
```

- [ ] **Step 6: Compile**
```bash
qmk compile -kb skatyl -km no_numrow
```
Expected: build succeeds. Common error: if you see `'DANCE_15' undeclared`, you removed it from the enum but left a reference somewhere — search for `DANCE_15` in the file.

- [ ] **Step 7: Commit**
```bash
git add keymaps/no_numrow/keymap.c
git commit -m "refactor: remove unreachable tap dances DANCE_15, DANCE_57, DANCE_59"
```

---

## Task 3: Rewrite DANCE_33 — $ on tap, ₹ on hold

The `on_dance_33` (rapid-fire function) and the step function logic are unchanged — only the keycodes swap from `LALT(KC_3)` to `KC_DLR`, and the hold case gains a Unicode send.

**Files:**
- Modify: `keymaps/no_numrow/keymap.c`

- [ ] **Step 1: Replace the `on_dance_33` body**

Replace:
```c
void on_dance_33(tap_dance_state_t *state, void *user_data) {
    if(state->count == 3) {
        tap_code16(LALT(KC_3));
        tap_code16(LALT(KC_3));
        tap_code16(LALT(KC_3));
    }
    if(state->count > 3) {
        tap_code16(LALT(KC_3));
    }
}
```
With:
```c
void on_dance_33(tap_dance_state_t *state, void *user_data) {
    if(state->count == 3) {
        tap_code16(KC_DLR);
        tap_code16(KC_DLR);
        tap_code16(KC_DLR);
    }
    if(state->count > 3) {
        tap_code16(KC_DLR);
    }
}
```

- [ ] **Step 2: Replace `dance_33_finished`**

Replace:
```c
void dance_33_finished(tap_dance_state_t *state, void *user_data) {
    dance_state.step = dance_33_dance_step(state);
    switch (dance_state.step) {
        case SINGLE_TAP: register_code16(LALT(KC_3)); break;
        case SINGLE_HOLD: register_code16(LALT(LSFT(KC_2))); break;
        case DOUBLE_TAP: register_code16(LALT(KC_3)); register_code16(LALT(KC_3)); break;
        case DOUBLE_SINGLE_TAP: tap_code16(LALT(KC_3)); register_code16(LALT(KC_3));
    }
}
```
With:
```c
void dance_33_finished(tap_dance_state_t *state, void *user_data) {
    dance_state.step = dance_33_dance_step(state);
    switch (dance_state.step) {
        case SINGLE_TAP: register_code16(KC_DLR); break;
        case SINGLE_HOLD: register_unicode(0x20B9); break;
        case DOUBLE_TAP: register_code16(KC_DLR); register_code16(KC_DLR); break;
        case DOUBLE_SINGLE_TAP: tap_code16(KC_DLR); register_code16(KC_DLR); break;
    }
}
```

- [ ] **Step 3: Replace `dance_33_reset`**

Replace:
```c
void dance_33_reset(tap_dance_state_t *state, void *user_data) {
    wait_ms(10);
    switch (dance_state.step) {
        case SINGLE_TAP: unregister_code16(LALT(KC_3)); break;
        case SINGLE_HOLD: unregister_code16(LALT(LSFT(KC_2))); break;
        case DOUBLE_TAP: unregister_code16(LALT(KC_3)); break;
        case DOUBLE_SINGLE_TAP: unregister_code16(LALT(KC_3)); break;
    }
    dance_state.step = 0;
}
```
With:
```c
void dance_33_reset(tap_dance_state_t *state, void *user_data) {
    wait_ms(10);
    switch (dance_state.step) {
        case SINGLE_TAP: unregister_code16(KC_DLR); break;
        case SINGLE_HOLD: break;
        case DOUBLE_TAP: unregister_code16(KC_DLR); break;
        case DOUBLE_SINGLE_TAP: unregister_code16(KC_DLR); break;
    }
    dance_state.step = 0;
}
```

> **Note on SINGLE_HOLD:** `register_unicode` sends a complete self-contained sequence — it does not leave a key registered in the HID state. The reset case is intentionally a no-op.

- [ ] **Step 4: Compile**
```bash
qmk compile -kb skatyl -km no_numrow
```
Expected: build succeeds. If you see `'register_unicode' undeclared`, check that `UNICODE_ENABLE = yes` is present in `keymaps/no_numrow/rules.mk`.

- [ ] **Step 5: Commit**
```bash
git add keymaps/no_numrow/keymap.c
git commit -m "feat: remap DANCE_33 to dollar/rupee ($ tap, Rs hold)"
```

---

## Task 4: Update Layer 1 layout keys

Five direct-key positions in the `[1]` layout array need replacing. No tap-dance logic changes — just the keycodes in the layout.

**Files:**
- Modify: `keymaps/no_numrow/keymap.c`

- [ ] **Step 1: Update the Layer 1 layout block**

Find the `[1] = LAYOUT(` block. Replace these five keys exactly:

| Find | Replace |
|---|---|
| `MT(KC_PSCR,LSFT(KC_3))` | `KC_PSCR` |
| `LALT(KC_RBRC),` | `KC_LABK,` |
| `LALT(LSFT(KC_RBRC)),` | `KC_RABK,` |
| `LALT(KC_LBRC),` | `KC_COLN,` |
| `LALT(LSFT(KC_LBRC)),` | `KC_QUES,` |

The three rows of Layer 1 should look like this after the edit:
```c
  [1] = LAYOUT(
  //-------------------------------------------------------------------------------        ------------------------------------------------------------------------------------
      KC_ESCAPE, KC_AT,        KC_PSCR,                TD(DANCE_31),         KC_PERC,              KC_CIRC,    KC_AMPR,    KC_ASTR,    KC_SCLN,    KC_BSPC,
  //-------------------------------------------------------------------------------        ------------------------------------------------------------------------------------
      KC_TAB,    KC_EQL,       KC_LABK,                KC_RABK,              TD(DANCE_32),         TD(BKSL_HME),LSFT(KC_LBRC),LSFT(KC_RBRC),TD(PIPE_END),KC_ENTER,
  //-------------------------------------------------------------------------------        ------------------------------------------------------------------------------------
      KC_TILD,   TD(DANCE_33), KC_COLN,                KC_QUES,              KC_DQUO,              KC_LBRC,    KC_LPRN,    KC_RPRN,    KC_RBRC,    TO(3),
  //-------------------------------------------------------------------------------        ------------------------------------------------------------------------------------
                        KC_BSPC,              TO(0),                OSM(MOD_LSFT),          KC_LALT,    TO(2),      KC_ENTER
  ),
```

- [ ] **Step 2: Compile**
```bash
qmk compile -kb skatyl -km no_numrow
```
Expected: build succeeds.

- [ ] **Step 3: Commit**
```bash
git add keymaps/no_numrow/keymap.c
git commit -m "feat: replace Mac curly-quote keys with <, >, :, ?, PSCR on Layer 1"
```

---

## Task 5: Update DANCE_31 and DANCE_32 hold actions

**Files:**
- Modify: `keymaps/no_numrow/keymap.c`

- [ ] **Step 1: Update `dance_31_finished` — screenshot shortcut**

Replace:
```c
        case SINGLE_HOLD: register_code16(LCTL(LGUI(LSFT(KC_4)))); break;
```
With:
```c
        case SINGLE_HOLD: register_code16(LGUI(LSFT(KC_S))); break;
```

- [ ] **Step 2: Update `dance_31_reset` to match**

Replace:
```c
        case SINGLE_HOLD: unregister_code16(LCTL(LGUI(LSFT(KC_4)))); break;
```
With:
```c
        case SINGLE_HOLD: unregister_code16(LGUI(LSFT(KC_S))); break;
```

- [ ] **Step 3: Update `dance_32_finished` — emoji picker**

Replace:
```c
        case SINGLE_HOLD: register_code16(LGUI(KC_QUOTE)); break;
```
With:
```c
        case SINGLE_HOLD: register_code16(LGUI(KC_PERIOD)); break;
```

- [ ] **Step 4: Update `dance_32_reset` to match**

Replace:
```c
        case SINGLE_HOLD: unregister_code16(LGUI(KC_QUOTE)); break;
```
With:
```c
        case SINGLE_HOLD: unregister_code16(LGUI(KC_PERIOD)); break;
```

- [ ] **Step 5: Compile**
```bash
qmk compile -kb skatyl -km no_numrow
```
Expected: build succeeds.

- [ ] **Step 6: Commit**
```bash
git add keymaps/no_numrow/keymap.c
git commit -m "feat: remap DANCE_31 hold to Win+Shift+S, DANCE_32 hold to Win+."
```

---

## Task 6: Update Layer 3 layout keys and DANCE_54/56/58 hold actions

**Files:**
- Modify: `keymaps/no_numrow/keymap.c`

- [ ] **Step 1: Update Layer 3 layout — browser back/forward**

Find the `[3] = LAYOUT(` block row 1. Replace:
```c
    TD(DANCE_54),   KC_MS_WH_LEFT,  KC_MS_UP,       KC_MS_WH_RIGHT, TD(DANCE_55),           LGUI(KC_LBRC),  LCTL(LSFT(KC_TAB)),   RCTL(KC_TAB),         LGUI(KC_RBRC),  KC_TRNS,
```
With:
```c
    TD(DANCE_54),   KC_MS_WH_LEFT,  KC_MS_UP,       KC_MS_WH_RIGHT, TD(DANCE_55),           KC_WBAK,        LCTL(LSFT(KC_TAB)),   RCTL(KC_TAB),         KC_WFWD,        KC_TRNS,
```
> If the build fails with `'KC_WBAK' undeclared`, use the long names `KC_WWW_BACK` and `KC_WWW_FORWARD` instead — same keycode, older QMK versions use different aliases.

- [ ] **Step 2: Update `dance_54_finished` — Alt+F4 instead of Mac Force Quit**

Replace:
```c
        case SINGLE_HOLD: register_code16(LALT(LGUI(KC_ESCAPE))); break;
```
With:
```c
        case SINGLE_HOLD: register_code16(LALT(KC_F4)); break;
```

- [ ] **Step 3: Update `dance_54_reset` to match**

Replace:
```c
        case SINGLE_HOLD: unregister_code16(LALT(LGUI(KC_ESCAPE))); break;
```
With:
```c
        case SINGLE_HOLD: unregister_code16(LALT(KC_F4)); break;
```

- [ ] **Step 4: Update `dance_56_finished` — Alt+Tab instead of Mac Cmd+Tab**

Replace:
```c
        case SINGLE_HOLD: register_code16(LGUI(KC_TAB)); break;
```
With:
```c
        case SINGLE_HOLD: register_code16(LALT(KC_TAB)); break;
```

- [ ] **Step 5: Update `dance_56_reset` to match**

Replace:
```c
        case SINGLE_HOLD: unregister_code16(LGUI(KC_TAB)); break;
```
With:
```c
        case SINGLE_HOLD: unregister_code16(LALT(KC_TAB)); break;
```

- [ ] **Step 6: Update `dance_58_finished` — Win+Tab Task View instead of Mac same-app switcher**

Replace:
```c
        case SINGLE_HOLD: register_code16(LGUI(KC_GRAVE)); break;
```
With:
```c
        case SINGLE_HOLD: register_code16(LGUI(KC_TAB)); break;
```

- [ ] **Step 7: Update `dance_58_reset` to match**

Replace:
```c
        case SINGLE_HOLD: unregister_code16(LGUI(KC_GRAVE)); break;
```
With:
```c
        case SINGLE_HOLD: unregister_code16(LGUI(KC_TAB)); break;
```

- [ ] **Step 8: Compile**
```bash
qmk compile -kb skatyl -km no_numrow
```
Expected: build succeeds.

- [ ] **Step 9: Commit**
```bash
git add keymaps/no_numrow/keymap.c
git commit -m "feat: remap Layer 3 browser keys and app-switcher dances for Windows"
```

---

## Task 7: Fix DANCE_60 and DANCE_63 stuck-key bugs

Both dances have mismatched `finished`/`reset` key pairs — the key registered on hold differs from the key unregistered, causing a stuck modifier after release. This task also converts them to their Windows equivalents.

**Files:**
- Modify: `keymaps/no_numrow/keymap.c`

- [ ] **Step 1: Update `dance_60_finished` — Ctrl+Left word-jump**

Replace:
```c
        case SINGLE_HOLD: register_code16(LALT(KC_LEFT)); break;
```
With:
```c
        case SINGLE_HOLD: register_code16(LCTL(KC_LEFT)); break;
```

- [ ] **Step 2: Fix `dance_60_reset` — was unregistering wrong key (LGUI instead of LALT)**

Replace:
```c
        case SINGLE_HOLD: unregister_code16(LGUI(KC_LEFT)); break;
```
With:
```c
        case SINGLE_HOLD: unregister_code16(LCTL(KC_LEFT)); break;
```

- [ ] **Step 3: Update `dance_63_finished` — KC_END end-of-line**

Replace:
```c
        case SINGLE_HOLD: register_code16(LGUI(KC_RIGHT)); break;
```
With:
```c
        case SINGLE_HOLD: register_code16(KC_END); break;
```

- [ ] **Step 4: Fix `dance_63_reset` — was unregistering wrong key (LALT instead of LGUI)**

Replace:
```c
        case SINGLE_HOLD: unregister_code16(LALT(KC_RIGHT)); break;
```
With:
```c
        case SINGLE_HOLD: unregister_code16(KC_END); break;
```

- [ ] **Step 5: Compile**
```bash
qmk compile -kb skatyl -km no_numrow
```
Expected: build succeeds.

- [ ] **Step 6: Commit**
```bash
git add keymaps/no_numrow/keymap.c
git commit -m "fix: correct stuck-key bugs in DANCE_60 and DANCE_63, remap to Ctrl+Left/End"
```

---

## Task 8: Flash and verify

- [ ] **Step 1: Enter bootloader mode on the right half**

Either method:
- **Plug-in:** Hold BOOT, plug in USB, release BOOT.
- **Two-button:** Hold BOOT, tap RESET, release BOOT.

- [ ] **Step 2: Flash right half**
```bash
qmk flash -kb skatyl -km no_numrow -bl uf2-split-right
```

- [ ] **Step 3: Flash left half** (same bootloader procedure)
```bash
qmk flash -kb skatyl -km no_numrow -bl uf2-split-left
```

- [ ] **Step 4: Install WinCompose** (required for ₹ key)

Download from https://github.com/samhocevar/wincompose/releases — install, launch, leave running in system tray. Default compose key (Right Alt) is fine; it won't conflict with the RALT home-row mod since WinCompose requires a full compose sequence, not just a bare RALT press.

- [ ] **Step 5: Manual verification checklist**

Test each changed key. Open a text editor and a browser.

**Layer 1 (hold Space+Shift to reach):**
| Key position | Expected output |
|---|---|
| R1C3 | PrintScreen captures full screen |
| R1C4 hold | Win+Shift+S opens Snipping Tool |
| R2C3 | `<` |
| R2C4 | `>` |
| R2C5 hold | Win+. opens emoji picker |
| R3C2 tap | `$` |
| R3C2 hold | `₹` (requires WinCompose running) |
| R3C3 | `:` |
| R3C4 | `?` |

**Layer 3 (reach via TO(3) from Layer 1 bottom-right):**
| Key | Expected |
|---|---|
| Top-left | Browser navigates back |
| Top-right | Browser navigates forward |
| DANCE_54 hold | Focused window closes (Alt+F4) |
| DANCE_56 hold | Alt+Tab app switcher opens |
| DANCE_58 hold | Win+Tab Task View opens |
| DANCE_60 hold | Cursor jumps one word left |
| DANCE_63 hold | Cursor jumps to end of line |
