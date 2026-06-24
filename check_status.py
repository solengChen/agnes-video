#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询视频生成状态

使用 video_id 或 task_id 查询视频生成进度
返回完整的任务信息和视频链接（如果生成完成）
"""

import os
import sys
import json
import subprocess
import argparse
import time
from datetime import datetime


def check_status(video_id, api_key=None, poll_interval=5, max_attempts=60):
    """
    查询视频生成状态
    
    Args:
        video_id: 视频 ID 或任务 ID
        api_key: API Key（可选）
        poll_interval: 轮询间隔（秒）
        max_attempts: 最大查询次数
    
    Returns:
        dict: 完整的任务状态信息
    """
    result = {
        'video_id': video_id,
        'query_time': datetime.now().isoformat(),
        'attempts': 0,
        'status': 'unknown',
        'video_url': None,
        'progress': None,
        'history': []
    }
    
    for attempt in range(1, max_attempts + 1):
        result['attempts'] = attempt
        result['last_check'] = datetime.now().isoformat()
        
        # 查询状态
        status_info = query_single_status(video_id, api_key)
        
        # 记录历史
        result['history'].append({
            'attempt': attempt,
            'timestamp': datetime.now().isoformat(),
            'status': status_info.get('status'),
            'progress': status_info.get('progress')
        })
        
        # 更新状态
        result['status'] = status_info.get('status', 'unknown')
        result['progress'] = status_info.get('progress')
        
        # 如果已完成或失败，停止查询
        if result['status'] in ['completed', 'failed', 'success']:
            result['video_url'] = status_info.get('video_url')
            result['metadata'] = status_info.get('metadata', {})
            break
        
        # 等待后继续查询
        if attempt < max_attempts:
            print(f"视频仍在生成中... (第 {attempt} 次查询)", file=sys.stderr)
            time.sleep(poll_interval)
    
    # 判断最终状态
    if result['status'] not in ['completed', 'failed', 'success']:
        result['status'] = 'timeout'
        result['suggestion'] = f'查询超时，请手动查询: agnes video status {video_id}'
    
    return result


def query_single_status(video_id, api_key=None):
    """
    单次查询状态
    
    Args:
        video_id: 视频 ID 或任务 ID
        api_key: API Key（可选）
    
    Returns:
        dict: 任务状态信息
    """
    # 准备命令
    cmd = ['agnes', 'video', 'status', video_id]
    
    if api_key:
        cmd.extend(['--api-key', api_key])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return parse_status_output(result.stdout, result.stderr)
        else:
            return {
                'status': 'error',
                'error': '查询失败',
                'stderr': result.stderr
            }
    
    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'error': '查询超时'
        }
    except FileNotFoundError:
        return {
            'status': 'error',
            'error': 'Agnes CLI 未安装',
            'suggestion': '运行: npm install -g @agnes-ai/agnes-cli'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def parse_status_output(stdout, stderr):
    """
    解析 Agnes CLI 状态输出
    """
    output = stdout + stderr
    result = {
        'status': 'unknown',
        'progress': None,
        'video_url': None,
        'metadata': {}
    }
    
    # 尝试从文本中提取状态信息
    output_lower = output.lower()
    
    if 'completed' in output_lower or 'success' in output_lower or '完成' in output:
        result['status'] = 'completed'
        result['progress'] = 100
    elif 'processing' in output_lower or '生成中' in output:
        result['status'] = 'processing'
    elif 'pending' in output_lower or '等待' in output:
        result['status'] = 'pending'
    elif 'failed' in output_lower or '失败' in output:
        result['status'] = 'failed'
    
    # 尝试提取视频 URL
    lines = output.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('http'):
            result['video_url'] = line
            break
        # 查找 URL 模式
        if '.mp4' in line or '.webm' in line:
            for word in line.split():
                if word.startswith('http') or '.mp4' in word or '.webm' in word:
                    result['video_url'] = word
                    break
    
    # 尝试 JSON 解析
    try:
        data = json.loads(output)
        if isinstance(data, dict):
            result['status'] = data.get('status', result['status'])
            result['progress'] = data.get('progress', result['progress'])
            result['video_url'] = data.get('video_url') or data.get('url')
            result['metadata'] = data
    except json.JSONDecodeError:
        pass
    
    return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='查询视频生成状态')
    parser.add_argument('video_id', help='视频 ID 或任务 ID')
    parser.add_argument('--api-key', '-k', help='API Key')
    parser.add_argument('--poll', '-p', action='store_true', help='持续轮询直到完成')
    parser.add_argument('--interval', '-i', type=int, default=5, help='轮询间隔（秒）')
    parser.add_argument('--max-attempts', '-m', type=int, default=60, help='最大查询次数')
    parser.add_argument('--no-poll', action='store_true', help='单次查询，不轮询')
    
    args = parser.parse_args()
    
    if args.no_poll:
        # 单次查询
        result = query_single_status(args.video_id, args.api_key)
    else:
        # 轮询查询
        result = check_status(
            args.video_id,
            api_key=args.api_key,
            poll_interval=args.interval,
            max_attempts=args.max_attempts
        )
    
    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 返回退出码
    if result.get('status') == 'completed':
        sys.exit(0)
    elif result.get('status') == 'failed':
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
