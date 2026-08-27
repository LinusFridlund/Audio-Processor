# DAC Module Bring-Up Notes

How to get a populated DAC board (ES9039Q2M) talking to the Raspberry Pi 5 and
producing real output, plus the gotchas hit along the way. Written after
getting the first board fully verified — use this as the checklist for the
second DAC board and any future ones.

## Physical wiring (jumper wires, pre-backplane)

No backplane board yet, so this is direct jumpers from the Pi's 40-pin header
to the DAC board's J6 connector.

**Ground — connect first, before any signal wires.** Every even pin on J6 is
tied to the board's GND. Used two separate ground jumpers rather than one, to
keep loop area down near each signal cluster:
- Pi physical pin 6 (GND) → a J6 even pin, near the I2C wires
- Pi physical pin 34 (GND) → a J6 even pin, near the I2S wires

**I2S:**

| Pi function | Pi physical pin | Pi BCM GPIO | J6 pin | J6 signal |
|---|---|---|---|---|
| BCLK | 12 | GPIO18 | 1 | I2S_BCLK |
| LRCLK/WS | 35 | GPIO19 | 3 | I2S_WCLK |
| DOUT (Pi→DAC) | 40 | GPIO21 | 5 | I2S_DATA |

**I2C:**

| Pi function | Pi physical pin | Pi BCM GPIO | J6 pin | J6 signal |
|---|---|---|---|---|
| SDA | 3 | GPIO2 | 11 | I2C_SDA |
| SCL | 5 | GPIO3 | 9 | I2C_SCL |

**Power:** ±15V_IN (J6 pins 19/17) from a bench/external supply — never from
the Pi. **DAC_EN (J6 pin 7):** left unconnected — the board's own pull-up
(R30) keeps the chip enabled by default.

## Raspberry Pi OS config

In `/boot/firmware/config.txt`:
```
dtparam=i2c_arm=on
dtparam=i2s=on
dtoverlay=hifiberry-dac
```
`hifiberry-dac` is the right overlay even though the chip isn't a
HiFiBerry/PCM5102A — it just tells the kernel "plain I2S DAC on the standard
pins," with no attempt to control it via I2C through ALSA. Since the chip is
configured over I2C by our own tooling (not through a kernel codec driver),
this keeps the kernel out of the way. Confirmed working via:
```
aplay -l
```
— shows up as `card 0: sndrpihifiberry`. The `pcm5102a-hifi-0` label in that
output is just the generic driver's internal naming, not a claim about the
actual chip.

## Gotcha #1: I2C address is 8-bit in the datasheet, 7-bit in Linux

The schematic's ADDR0/ADDR1 table lists addresses as 0x90/0x92/0x94/0x96 —
these are 8-bit addresses including the R/W bit. `i2cdetect`/`i2c-tools` use
7-bit addressing. With both ADDR pins at GND (default), the real address to
look for is **0x48**, not 0x90.
```
sudo apt install -y i2c-tools     # i2cdetect isn't installed by default
sudo i2cdetect -y 1               # should show 48
```

## Gotcha #2: the chip does nothing until you write two registers

I2C responding and I2S clocking cleanly (`speaker-test` running with no
errors) is not the same as the chip actually producing output — confirmed
0V at the connector despite both of those working. Two non-default register
writes were required:

**1. Register 0 (SYSTEM CONFIG), bit 1 — DAC_MODE.** Defaults to 0 (DAC
disabled) — the entire analog section is off until this is set, regardless of
anything else being correct.
```
sudo i2cset -y 1 0x48 0x00 0x02
```

**2. Register 61 (TDM CONFIG2), bits [6:5] — TDM_BIT_WIDTH.** Defaults to
32-bit slots. I2S is handled through the same slot-based decoder as TDM on
this chip, so if the Pi is sending a different bit depth than the chip
expects, the clock looks fine but the decoder never sees valid frames. Fixed
by forcing the Pi to send 32-bit frames rather than changing the register:
```
speaker-test -D hw:0,0 -c2 -t sine -f 1000 -l 0 -F S32_LE -r 44100
```
(Alternative: write `0xA0` to register `0x3D` to set the chip to 16-bit
instead, if forcing 32-bit from the Pi side isn't convenient.)

Both writes are volatile — they do **not** persist across a power cycle.
Whatever init sequence ends up in `audio_engine` needs to send these (and
presumably a few more) every time the board powers up.

## Verifying without a speaker connected

None of this requires audio equipment to be hooked up — useful since a
speaker cable wasn't available during bring-up.

Check the kernel sees the device (no playback needed):
```
aplay -l
cat /proc/asound/cards
```

Play a tone regardless of what's connected to the output — the point is
exercising the digital path, not listening:
```
speaker-test -D hw:0,0 -c2 -t sine -f 1000 -l 0
```

Useful registers to read back while a tone plays (all via
`i2cget -y 1 0x48 <reg>`):

| Register | Address | Purpose | Expected when healthy |
|---|---|---|---|
| CHIP ID READ | `0xE1` | Sanity check that reads work at all | `0x63` |
| SYSTEM CONFIG | `0x00` | Confirms DAC_MODE write stuck | `0x02` |
| AUTOMUTE READ | `0xF2` | Per-channel automute state | `0x00` |
| INPUT STREAM READBACK | `0xF5` | Bit 3 = TDM_DATA_VALID | bit 3 set (e.g. `0x08`) |
| INTERRUPT SOURCES | `0xE5` | Bit 7 = BCK/WS validity | `0x00` (no fail) |
| INPUT SELECTION | `0x39` | Format select (0x40 = default, PCM, no auto-detect) | `0x40` is fine as-is |

## Reading the multimeter output correctly

`speaker-test` alternates channels (L, then R, then back to L) rather than
playing both continuously — a ~3s-on/3s-off AC reading on one channel's
connector is this cycling, **not a fault**. Confirmed by probing the other
channel at the same time and seeing it complementary (on when the first is
off). For a steady, non-alternating tone on both channels at once (easier for
probing), use a real test file instead:
```
sudo apt install -y sox
sox -n test.wav synth 30 sine 1000 sine 1000
aplay -D hw:0,0 test.wav
```

## Summary checklist for the next board

1. Wire ground first, then I2S, then I2C, per the tables above.
2. Power ±15V independently; leave DAC_EN unconnected.
3. Enable i2c_arm and i2s, add the hifiberry-dac overlay, reboot.
4. `i2cdetect -y 1` → expect `0x48`.
5. `aplay -l` → expect `sndrpihifiberry`.
6. Play a tone, then `i2cset` DAC_MODE on and confirm bit width matches
   what's actually being sent (check `/proc/asound/card0/pcm0p/sub0/hw_params`
   if unsure).
7. Confirm via `0xF5` (TDM_DATA_VALID) and multimeter/real load, remembering
   the channel-alternation behavior above.
