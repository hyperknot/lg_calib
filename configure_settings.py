#!/usr/bin/env python

import asyncio
import time

from bscpylgtv import WebOsClient


HOST = '192.168.1.12'

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
    'colorTemperature': '50',
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
        'colorTemperature': '-50',
        'hdrDynamicToneMapping': 'off',
        'peakBrightness': 'high',
        'gamma': 'medium',
        'whiteBalanceMethod': '22code',
        'whiteBalanceRed': [
            0,
            2,
            0,
            1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -1,
            -2,
            -2,
            -2,
            -1,
            -1,
            -2,
            0,
            0,
        ],
        'whiteBalanceGreen': [1, 2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, -2, -2, 0, 0, 0, 0, 0, 0],
        'whiteBalanceBlue': [-1, 1, -1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 5, 5, 5, 3, 4, 4, 0, 0],
        'whiteBalancePoint': 'low',
        'whiteBalanceRedOffset': '0',
        'whiteBalanceGreenOffset': '0',
        'whiteBalanceBlueOffset': '0',
        'whiteBalanceRedGain': '0',
        'whiteBalanceGreenGain': '0',
        'whiteBalanceBlueGain': '0',
        'whiteBalanceCodeValue': '20',
    },
}


OVERRIDES = {
    'SDR': {
        'vivid': {},
        'normal': {},
        'eco': {'backlight': '0', 'colorGamut': 'native'},
        'sports': {},
        'game': {'gamma': 'medium'},
        'filmMaker': {},
        'cinema': {'backlight': '84', 'colorGamut': 'native'},
        'expert1': {'backlight': '43', 'gamma': 'medium', 'colorGamut': 'native'},
        'expert2': {'colorGamut': 'native'},
    },
    'HDR': {
        'hdrVivid': {},
        'hdrStandard': {},
        'hdrCinemaBright': {},
        'hdrGame': {'hdrDynamicToneMapping': 'HGIG'},
        'hdrCinema': {},
        'hdrFilmMaker': {},
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
    commands = []
    for mode, settings in OVERRIDES[mode_type].items():
        commands.extend(
            [
                ('set_current_picture_mode', [mode]),
                ('set_current_picture_settings', [{**base_settings, **settings}]),
                COMMAND_AI_OFF,
            ]
        )
    default_mode = 'eco' if mode_type == 'SDR' else 'hdrStandard'
    commands.append(('set_current_picture_mode', [default_mode]))
    asyncio.run(run_commands(commands))


if __name__ == '__main__':
    asyncio.run(run_commands([('button', ['INFO'])]))
    configure_modes('SDR')
    configure_modes('HDR')
