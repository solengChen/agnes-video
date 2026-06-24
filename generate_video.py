#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建视频生成任务

使用 Agnes AI Video V2.0 模型创建视频生成任务
返回包含 task_id 和 video_id 的完整响应信息
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path


def validate_num_frames(num_frames):
    """
    验证帧数是否符合要求
    必须是 8n + 1，且 <= 441
    """
    if num_frames > 441:
        return False
    if num_frames < 1:
        return False
    return (num_frames - 1) % 8 == 0


def calculate_duration(num_frames, frame_rate):
    """计算视频时长（秒）"""
    return num_frames / frame_rate if frame_rate > 0 else 0


def generate_video(prompt, num_frames=121, frame_rate=24, api_key=None, images=None, mode='normal'):
    """
    生成视频
    
    Args:
        prompt: 视频描述
        num_frames: 帧数（必须是 16 的倍数 + 1）
        frame_rate: 帧率
        api_key: API Key（可选）
        images: 关键帧图片路径列表
        mode: 生成模式 ('normal' 或 'keyframes')
    
    Returns:
        dict: 包含 task_id 和 video_id 的响应
    """
    # 验证帧数
    if not validate_num_frames(num_frames):
        valid_values = [1, 17, 33, 49, 65, 81, 97, 113, 121, 241, 361]
        closest = min([v for v in valid_values if v >= num_frames], default=121)
        return {
            'success': False,
            'error': f'num_frames 必须是 16 的倍数 + 1',
            'valid_examples': valid_values,
            'current_value': num_frames,
            'suggested_value': closest
        }
    
    # 计算视频时长
    duration = calculate_duration(num_frames, frame_rate)
    
    # 准备命令
    cmd = 'agnes video generate'
    
    # 添加 prompt
    cmd += f' --prompt "{prompt}"'
    
    # 添加帧数和帧率
    cmd += f' --num-frames {num_frames}'
    cmd += f' --frame-rate {frame_rate}'
    
    # 如果有 API Key
    if api_key:
        cmd += f' --api-key "{api_key}"'
    
    # 如果是关键帧模式
    if mode == 'keyframes' and images:
        cmd += f' --mode keyframes'
        for img in images:
            cmd += f' --image "{img}"'
    
    # 执行命令
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            shell=True
        )
        
        if result.returncode == 0:
            # 解析输出
            output = result.stdout.strip()
            return parse_agnes_output(output, prompt, num_frames, frame_rate, duration, mode)
        else:
            # 解析错误
            error_output = result.stderr.strip()
            
            # 检查是否任务已提交成功（即使有后续错误）
            if 'Task submitted:' in error_output or 'Task submitted' in error_output:
                # 尝试从输出中提取 video_id
                video_id = None
                task_id = None
                
                for line in error_output.split('\n'):
                    if 'video_id:' in line or 'video_' in line:
                        # 提取 video_id
                        import re
                        match = re.search(r'video_[a-zA-Z0-9]+', line)
                        if match:
                            video_id = match.group(0)
                    if 'Task submitted:' in line or 'Task submitted' in line:
                        # 提取 task_id
                        import re
                        match = re.search(r'video_[a-zA-Z0-9]+', line)
                        if match:
                            task_id = match.group(0)
                
                # 尝试解析 JSON 状态
                status = None
                progress = None
                video_url = None
                
                for line in error_output.split('\n'):
                    if line.strip().startswith('{'):
                        try:
                            json_data = json.loads(line)
                            if 'error' in json_data:
                                # 这是一个错误响应，检查是否是速率限制
                                error_info = json_data.get('error', {})
                                if error_info.get('subtype') == 'rate_limited':
                                    # 速率限制，但任务已提交
                                    status = 'submitted'
                                    progress = 'unknown'
                        except:
                            pass
                    elif 'Status:' in line:
                        status = line.split('Status:')[1].strip()
                    elif 'Progress:' in line:
                        progress = line.split('Progress:')[1].strip()
                
                return {
                    'success': True,
                    'message': '视频生成任务已提交',
                    'video_id': video_id,
                    'task_id': task_id,
                    'status': status,
                    'progress': progress,
                    'note': '视频正在生成中，遇到了 API 速率限制，请稍后查询状态',
                    'raw_output': error_output
                }
            
            return {
                'success': False,
                'error': '视频生成任务创建失败',
                'stderr': error_output,
                'suggestion': '请检查 API Key 是否正确配置'
            }
    
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': '命令执行超时',
            'suggestion': '请检查网络连接或重试'
        }
    except FileNotFoundError:
        return {
            'success': False,
            'error': 'Agnes CLI 未安装',
            'suggestion': '运行: npm install -g @agnes-ai/agnes-cli'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'suggestion': '请检查系统配置'
        }


def check_agnes_available():
    """检查 Agnes CLI 是否可用"""
    import os
    # 尝试多种方式
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
            import subprocess
            result = subprocess.run(
                [cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=5,
                shell=False
            )
            if result.returncode == 0:
                return True
        except:
            continue
    
    # 尝试 shell 方式
    try:
        import subprocess
        result = subprocess.run(
            'agnes --version',
            capture_output=True,
            text=True,
            timeout=5,
            shell=True
        )
        return result.returncode == 0
    except:
        return False
    
    return False


def parse_agnes_output(stdout, prompt, num_frames, frame_rate, duration, mode):
    """
    解析 Agnes CLI 输出
    Agent 友好输出：成功时只输出 URL，但我们需要获取更多信息
    """
    result = {
        'success': True,
        'task_submitted': True,
        'prompt': prompt,
        'parameters': {
            'num_frames': num_frames,
            'frame_rate': frame_rate,
            'duration': round(duration, 2),
            'mode': mode
        },
        'raw_output': stdout,
        'status': 'pending',
        'video_id': None,
        'task_id': None,
        'video_url': None
    }
    
    # 尝试从输出中提取 video_id 和 task_id
    lines = stdout.split('\n')
    for line in lines:
        line = line.strip()
        if 'video_id' in line.lower() or line.startswith('vid_'):
            result['video_id'] = extract_id(line, 'vid_')
        elif 'task_id' in line.lower() or line.startswith('task_'):
            result['task_id'] = extract_id(line, 'task_')
        elif line.startswith('http'):
            result['video_url'] = line
    
    # 如果没有提取到，尝试 JSON 解析
    if not result['video_id']:
        try:
            data = json.loads(stdout)
            if isinstance(data, dict):
                result['video_id'] = data.get('video_id') or data.get('id')
                result['task_id'] = data.get('task_id') or data.get('taskId')
                result['video_url'] = data.get('video_url') or data.get('url')
        except json.JSONDecodeError:
            pass
    
    # 生成查询命令
    if result['video_id']:
        result['check_command'] = f"agnes video status {result['video_id']}"
        result['check_script'] = f"python {__file__.replace('generate_video.py', 'check_status.py')} {result['video_id']}"
    
    return result


def extract_id(text, prefix):
    """从文本中提取 ID"""
    if prefix in text:
        parts = text.split(prefix)
        if len(parts) > 1:
            id_part = parts[1].split()[0].strip()
            return f"{prefix}{id_part}"
    return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='使用 Agnes AI 生成视频')
    parser.add_argument('--prompt', '-p', required=True, help='视频描述文本')
    parser.add_argument('--num-frames', '-n', type=int, default=121, help='视频帧数（必须是 16 的倍数 + 1）')
    parser.add_argument('--frame-rate', '-f', type=int, default=24, help='帧率 (fps)')
    parser.add_argument('--api-key', '-k', help='API Key')
    parser.add_argument('--image', '-i', action='append', help='关键帧图片路径')
    parser.add_argument('--mode', '-m', default='normal', choices=['normal', 'keyframes'], help='生成模式')
    
    args = parser.parse_args()
    
    # 生成视频
    result = generate_video(
        prompt=args.prompt,
        num_frames=args.num_frames,
        frame_rate=args.frame_rate,
        api_key=args.api_key,
        images=args.image,
        mode=args.mode
    )
    
    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 返回退出码
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
