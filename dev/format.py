import os

####################################################################################################

def table_formater(text: str):

    table_keys = []
    table = {}
    for line in text.splitlines():
        if not line.strip():
            new_row = True
        elif new_row:
            key = line.strip().lower()
            table_keys.append(key)
            table[key] = []
            new_row = False
        else:
            table[key].append(line)
    print(table_keys)
    print(table)

    group_key = table_keys[0]
    number_of_columns = len(table[group_key])
    print('...:')
    for i in range(number_of_columns):
        value = table[group_key][i].replace(' ', ' | ')
        print(f'  {value}:')
        for key in table_keys[1:]:
            value = table[key][i]
            print(f'    {key} : {value}')

def format_list(text: str):
    output = ''
    level = 0
    for line in text.splitlines():
        line = line.strip()
        if line == '•':
            level = 1
            output += os.linesep + ' - '
        elif line == '–':
            level = 2
            output += os.linesep + '  - '
        else:
            output += line
    print(output)

####################################################################################################

text  = '''
Devices
AVR32DA28 AVR32DA32 AVR32DA48
AVR64DA28 AVR64DA32 AVR64DA48 AVR64DA64
AVR128DA28 AVR128DA32 AVR128DA48 AVR128DA64

Flash Memory
32 KB
64 KB
128 KB

SRAM
4 KB
8 KB
16 KB

EEPROM
512B
512B
512B

User Row
32B
32B
32B
'''

####################################################################################################

text='''
Devices
AVR128DA28 AVR64DA28 AVR32DA28
AVR128DA32 AVR64DA32 AVR32DA32
AVR128DA48 AVR64DA48 AVR32DA48
AVR128DA64 AVR64DA64

Pins
28
32
48
64

Max. Frequency (MHz)
24
24
24
24

16-bit Timer/Counter type A (TCA)
1
1
2
2

16-bit Timer/Counter type B (TCB)
3
3
4
5

12-bit Timer/Counter type D (TCD)
1
1
1
1

Real-Time Counter (RTC)
1
1
1
1

USART
3
3
5
6

SPI
2
2
2
2

TWI/I2C
1
2
2
2

12-bit Differential ADC (channels)
1 (10)
1 (14)
1 (18)
1 (22)

10-bit DAC (outputs)
1
1
1
1

Analog Comparator (AC)
3
3
3
3

Zero-Cross Detectors (ZCD)
1
1
2
3

Peripheral Touch Controller (PTC) (self-cap/mutual cap channels)
1 (18/81)
1 (22/121)
1 (32/256)
1 (46/529)

Configurable Custom Logic (CCL)
1 (4)
1 (4)
1 (6)
1 (6)

Watchdog Timer (WDT)
1
1
1
1

Event System channels
8
8
10
10

General Purpose I/O
23
27
41
55

PORT
PA[7:0], PC[3:0], PD[7:0], PF[6,1,0]
PA[7:0], PC[3:0], PD[7:0],PF[6:0]
PA[7:0], PB[5:0], PC[7:0], PD[7:0], PE[3:0], PF[6:0]
PA[7:0], PB[7:0], PC[7:0], PD[7:0], PE[7:0], PF[6:0], PG[7:0]

External Interrupts
23
27
41
55

CRCSCAN
1
1
1
1

Unified Program and Debug Interface (UPDI)
1
1
1
1
'''

# table_formater(text)

####################################################################################################

text = '''
•
AVR® CPU
–
Running at up to 24 MHz
–
Single-cycle I/O access
–
Two-level interrupt controller
–
Two-cycle hardware multiplier
–
Supply voltage range: 1.8V to 5.5V
•
Memories
–
128 KB In-System self-programmable Flash memory
–
512B EEPROM
–
16 KB SRAM
–
32B of user row in nonvolatile memory that can keep data during chip-erase and be programmed while the
device is locked
–
Write/erase endurance
•
Flash 10,000 cycles
•
EEPROM 100,000 cycles
–
Data retention: 40 years at 55°C
•
System
–
Power-on Reset (POR) circuit
–
Brown-out Detector (BOD)
–
Clock options
•
High-Precision internal high-frequency Oscillator with selectable frequency up to 24 MHz (OSCHF)
–
Auto-tuning for improved internal oscillator accuracy
•
Internal PLL up to 48 MHz for high-frequency operation of Timer/Counter type D (PLL)
•
32.768 kHz Ultra-Low Power internal oscillator (OSC32K)
•
32.768 kHz external crystal oscillator (XOSC32K)
•
External clock input
–
Single-pin Unified Program and Debug Interface (UPDI)
–
Three sleep modes
•
Idle with all peripherals running for immediate wake-up
•
Standby with a configurable operation of selected peripherals
•
Power-Down with full data retention
•
Peripherals
–
Up to two 16-bit Timer/Counter type A (TCA) with a dedicated period register and three PWM channels
–
Up to five 16-bit Timer/Counter type B (TCB) with input capture and simple PWM functionality
–
One 12-bit Timer/Counter type D (TCD) optimized for power control
–
One 16-bit Real-Time Counter (RTC) running from an external crystal or internal oscillator
–
Up to six USART with fractional baud rate generator, auto-baud, and start-of-frame detection
–
Two host/client Serial Peripheral Interface (SPI)
–
Up to two Two-Wire Interface (TWI) with dual address match
•
Independent host and client operation (Dual mode)
•
Philips I2C compatible
•
Standard mode (Sm, 100 kHz)
•
Fast mode (Fm, 400 kHz)
•
Fast mode plus (Fm+, 1 MHz) (1)

–
Event System for CPU independent and predictable inter-peripheral signaling
–
Configurable Custom Logic (CCL) with up to six programmable Look-up Tables (LUT)
–
One 12-bit differential 130 ksps Analog-to-Digital Converter (ADC)
–
Three Analog Comparators (ACs) with window compare functions

–
One 10-bit Digital-to-Analog Converter (DAC)
–
Up to three Zero-Cross Detectors (ZCD)
–
Multiple voltage references (VREF)
•
1.024V
•
2.048V
•
2.500V
•
4.096V
–
Peripheral Touch Controller (PTC) with Driven Shield+ and Boost Mode technologies for capacitive touch
buttons, sliders, wheels and 2D surface
•
Up to 46 self-capacitance and 529 mutual capacitance channels
–
Automated Cyclic Redundancy Check (CRC) Flash memory scan
–
Watchdog Timer (WDT) with Window mode, with a separate on-chip oscillator
–
External interrupt on all general purpose pins
•
I/O and Packages:
–
Up to 55 programmable I/O pins
–
28-pin SPDIP, SSOP and SOIC
–
32-pin VQFN 5x5 mm and TQFP 7x7 mm
–
48-pin VQFN 6x6 mm and TQFP 7x7 mm
–
64-pin VQFN 9x9 mm and TQFP 10x10 mm
•
Temperature Ranges:
–
Industrial: -40°C to +85°C
–
Extended: -40°C to +125°C

'''
