#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 Agnes API Key 配置状态

检查 API Key 是否已配置，支持以下优先级：
1. 环境变量 AGNES_API_KEY
2. 本地保存的 Key (agnes key set)
3. 命令行参数 --api-key
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def check_env_key():
    """检查环境变量中的 API Key"""
    api_key = os.environ.get('AGNES_API_KEY', '')
    if api_key:
        return {'source': 'environment', 'configured': True, 'prefix': api_key[:8] + '...' if len(api_key) > 8 else '***'}
    return {'source': 'environment', 'configured': False}


def check_saved_key():
    """检查本地保存的 Key"""
    try:
        # 尝试运行 agnes key status
        result = subprocess.run(
            ['agnes', 'key', 'status'],
            capture_output=True,
            text=True,
            timeout=5,
            shell=True
        )
        output = result.stdout + result.stderr
        # 检查多种可能的成功状态
        if result.returncode == 0 and any(status in output for status in ['configured', 'API Key configured', '"status": "configured"']):
            return {'source': 'saved', 'configured': True}
        return {'source': 'saved', 'configured': False}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {'source': 'saved', 'configured': False, 'error': 'agnes CLI not found'}


def check_agnes_installed():
    """检查 Agnes CLI 是否已安装"""
    # 尝试多种方式查找 agnes 命令
    commands = ['agnes', 'agnes.cmd']
    
    # Windows 特定路径
    if os.name == 'nt':
        npm_global = os.path.join(os.environ.get('APPDATA', ''), 'npm')
        if os.path.exists(npm_global):
            agnes_exe = os.path.join(npm_global, 'agnes.cmd')
            if os.path.exists(agnes_exe):
                commands.insert(0, agnes_exe)
    
    for cmd in commands:
        try:
            result = subprocess.run(
                [cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=5,
                shell=False
            )
            if result.returncode == 0:
                return {'installed': True, 'version': result.stdout.strip()}
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue
    
    # 如果标准方式失败，尝试 shell 方式
    try:
        result = subprocess.run(
            'agnes --version',
            capture_output=True,
            text=True,
            timeout=5,
            shell=True
        )
        if result.returncode == 0:
            return {'installed': True, 'version': result.stdout.strip()}
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    
    return {'installed': False}


def main():
    """主函数"""
    result = {
        'status': 'checking',
        'api_key_configured': False,
        'agnes_installed': False,
        'recommendations': []
    }
    
    # 检查 Agnes CLI 安装状态
    agnes_status = check_agnes_installed()
    result['agnes_installed'] = agnes_status['installed']
    if agnes_status.get('version'):
        result['agnes_version'] = agnes_status['version']
    
    if not agnes_status['installed']:
        result['recommendations'].append({
            'type': 'install',
            'message': 'Agnes CLI 未安装',
            'action': '运行命令: npm install -g @agnes-ai/agnes-cli'
        })
    
    # 检查 API Key 配置
    env_status = check_env_key()
    saved_status = check_saved_key()
    
    result['api_key_configured'] = env_status['configured'] or saved_status['configured']
    result['api_key_source'] = None
    
    if env_status['configured']:
        result['api_key_source'] = 'environment'
        result['api_key_prefix'] = env_status.get('prefix')
    elif saved_status['configured']:
        result['api_key_source'] = 'saved'
    
    if not result['api_key_configured']:
        result['recommendations'].append({
            'type': 'api_key',
            'message': 'API Key 未配置',
            'actions': [
                '1. 访问 https://agnes-ai.com 注册账号并申请 API Key',
                '2. 或者运行命令: agnes key register',
                '3. 保存 API Key: agnes key set "您的_API_KEY"',
                '4. 验证配置: agnes key status'
            ]
        })
    
    result['status'] = 'ready' if (result['agnes_installed'] and result['api_key_configured']) else 'not_ready'
    
    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 返回退出码
    sys.exit(0 if result['status'] == 'ready' else 1)


if __name__ == '__main__':
    main()
