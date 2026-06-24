#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agnes Video - AI 视频生成技能

基于 Agnes AI Video V2.0 模型的 AI 视频生成技能
支持文本生成视频、关键帧动画等功能

版本: 1.0.0
更新日期: 2026-06-25
"""

__version__ = '1.0.0'
__author__ = 'AI Assistant'

# 技能元数据
SKILL_METADATA = {
    'name': 'agnes-video',
    'version': '1.0.0',
    'description': '使用 Agnes AI Video V2.0 模型生成 AI 视频',
    'author': __author__,
    'platform': 'Agnes AI',
    'models': ['agnes-video-v2.0'],
    'capabilities': [
        'text-to-video',
        'keyframe-animation',
        'async-task-management'
    ]
}

# 导出主要类和函数
from .video_manager import AgnesVideoManager
from .generate_video import generate_video, validate_num_frames, calculate_duration
from .check_status import check_status, query_single_status
from .check_api_key import check_agnes_installed, check_env_key, check_saved_key

__all__ = [
    'AgnesVideoManager',
    'generate_video',
    'validate_num_frames',
    'calculate_duration',
    'check_status',
    'query_single_status',
    'check_agnes_installed',
    'check_env_key',
    'check_saved_key',
    'SKILL_METADATA'
]
