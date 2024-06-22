#!/usr/bin/env python

import asyncio
import json
import time
from pathlib import Path

import click

from bscpylgtv import WebOsClient


HOST = '192.168.1.12'

DEFAULT_SDR_MODE = 'expert2'
DEFAULT_HDR_MODE = 'hdrFilmMaker'
DEFAULT_DOVI_MODE = 'dolbyHdrCinema'

try:
    CUSTOM_WB_HDR = json.load(open(Path('data') / 'wb_hdr.json'))
except Exception:
    CUSTOM_WB_HDR = {}

try:
    CUSTOM_WB_DOVI = json.load(open(Path('data') / 'wb_dovi.json'))
except Exception:
    CUSTOM_WB_DOVI = {}

COMMAND_AI_OFF = (
    'set_current_picture_settings',
    [
        {
            'ai_Picture': 'off',
            'ai_Brightness': 'off',
            'ai_Genre': 'off',
        },
        'aiPicture',
    ],
)

COMMON_SETTINGS = {
    'backlight': '34',
    'contrast': '85',
    'brightness': '50',
    'dynamicContrast': 'off',
    'peakBrightness': 'off',
    'gamma': 'high1',
    'motionEyeCare': 'off',
    'color': '50',
    'colorGamut': 'auto',
    'dynamicColor': 'off',
    'colorTemperature': '-45',  # -50 => Warm 50
    'sharpness': '0',
    'superResolution': 'off',
    'noiseReduction': 'off',
    'mpegNoiseReduction': 'off',
    'smoothGradation': 'off',
    'realCinema': 'on',
    'truMotionMode': 'off',
}

MODE_SETTINGS = {
    'SDR': {**COMMON_SETTINGS},
    'HDR': {
        **COMMON_SETTINGS,
        'backlight': '100',
        'contrast': '100',
        'peakBrightness': 'high',
        'gamma': 'medium',
        'hdrDynamicToneMapping': 'off',
        **CUSTOM_WB_HDR,
    },
    'DOVI': {
        **COMMON_SETTINGS,
        'backlight': '100',
        'contrast': '100',
        'peakBrightness': 'high',
        'gamma': 'medium',
        'colorGamut': 'native',
        'dolbyPrecisionDetail': 'off',
    },
}

OVERRIDES = {
    'SDR': {
        # 'vivid': {},
        # 'normal': {},
        # 'eco': {},
        # 'sports': {},
        # 'game': {'gamma': 'medium'},
        # 'filmMaker': {},
        # 'cinema': {'backlight': '84', 'colorGamut': 'native'},
        # 'expert1': {'backlight': '43', 'gamma': 'medium', 'colorGamut': 'native'},
        'expert2': {},
    },
    'HDR': {
        # 'hdrVivid': {},
        # 'hdrStandard': {},
        # 'hdrCinemaBright': {},
        # 'hdrGame': {'hdrDynamicToneMapping': 'HGIG'},
        # 'hdrCinema': {},
        'hdrFilmMaker': {},
    },
    'DOVI': {
        # 'dolbyHdrVivid': {},
        # 'dolbyHdrStandard': {},
        # 'dolbyHdrGame': {},
        'dolbyHdrCinemaBright': {},
        'dolbyHdrCinema': {},
    },
}


async def run_commands(commands):
    client = await WebOsClient.create(HOST, ping_interval=None, states=None, calibration_info=None)
    await client.connect()

    for command, params in commands:
        if command == 'set_current_picture_mode':
            print(command, params[0])
        try:
            result = await getattr(client, command)(*params)
            print(f'  Command: {command}')
            print(f'    Result: {result}')
        except Exception as e:
            print(f'Error executing {command}: {e}')
        time.sleep(3)

    await client.disconnect()


def configure_modes(mode_type):
    base_settings = MODE_SETTINGS[mode_type]
    commands = [('button', ['INFO'])]

    for mode, settings in OVERRIDES[mode_type].items():
        commands.extend(
            [
                ('set_current_picture_mode', [mode]),
                ('set_current_picture_settings', [{**base_settings, **settings}]),
                COMMAND_AI_OFF,
            ]
        )

    default_mode = {
        'SDR': DEFAULT_SDR_MODE,
        'HDR': DEFAULT_HDR_MODE,
        'DOVI': DEFAULT_DOVI_MODE,
    }[mode_type]

    commands.append(('set_current_picture_mode', [default_mode]))

    asyncio.run(run_commands(commands))


@click.group()
def cli():
    pass


@cli.command()
def sdr():
    """Configure SDR mode."""
    configure_modes('SDR')


@cli.command()
def hdr():
    """Configure HDR mode."""
    configure_modes('HDR')


@cli.command()
def dovi():
    """Configure DOVI mode."""
    configure_modes('DOVI')


if __name__ == '__main__':
    cli()
