#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agnes Video 统一管理工具

整合 API Key 检查、视频生成、状态查询等功能
提供统一的命令行接口
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

# 导入同目录下的模块
sys.path.insert(0, str(Path(__file__).parent))
from check_api_key import check_agnes_installed, check_env_key, check_saved_key
from generate_video import generate_video, validate_num_frames, calculate_duration
from check_status import check_status, query_single_status


class AgnesVideoManager:
    """Agnes Video 统一管理器"""
    
    def __init__(self):
        self.status = self.check_system_status()
    
    def check_system_status(self):
        """检查系统状态"""
        status = {
            'ready': True,
            'issues': []
        }
        
        # 检查 Agnes CLI
        agnes = check_agnes_installed()
        if not agnes['installed']:
            status['ready'] = False
            status['issues'].append({
                'type': 'missing_cli',
                'message': 'Agnes CLI 未安装',
                'solution': '运行: npm install -g @agnes-ai/agnes-cli'
            })
        
        # 检查 API Key
        env_key = check_env_key()
        saved_key = check_saved_key()
        
        if not (env_key['configured'] or saved_key['configured']):
            status['ready'] = False
            status['issues'].append({
                'type': 'missing_api_key',
                'message': 'API Key 未配置',
                'solutions': [
                    '1. 访问 https://agnes-ai.com 注册账号并申请 API Key',
                    '2. 运行: agnes key register',
                    '3. 保存: agnes key set "您的_API_KEY"',
                    '4. 验证: agnes key status'
                ]
            })
        else:
            status['api_key_source'] = 'environment' if env_key['configured'] else 'saved'
        
        return status
    
    def check_api_key(self):
        """检查 API Key 配置"""
        print("🔍 检查系统配置...")
        print()
        
        if self.status['ready']:
            print("✅ 系统已就绪")
            print(f"   API Key 来源: {self.status.get('api_key_source', 'unknown')}")
        else:
            print("❌ 系统未就绪")
            for issue in self.status['issues']:
                print(f"\n⚠️  {issue['message']}")
                if 'solution' in issue:
                    print(f"   解决: {issue['solution']}")
                if 'solutions' in issue:
                    for sol in issue['solutions']:
                        print(f"   {sol}")
        
        return self.status['ready']
    
    def guide_api_key_setup(self):
        """引导 API Key 配置"""
        print("\n📝 API Key 配置指南")
        print("=" * 50)
        print()
        print("步骤 1: 获取 API Key")
        print("   • 访问: https://agnes-ai.com")
        print("   • 注册账号并登录")
        print("   • 在个人中心申请 API Key")
        print()
        print("步骤 2: 保存 API Key")
        print("   方式 A: 使用 Agnes CLI")
        print("      agnes key register  # 打开注册页面")
        print("      agnes key set \"您的_API_KEY\"")
        print()
        print("   方式 B: 使用环境变量")
        print("      Windows PowerShell:")
        print("      $env:AGNES_API_KEY = \"您的_API_KEY\"")
        print()
        print("   方式 C: 设置永久环境变量")
        print("      [System.Environment]::SetEnvironmentVariable(")
        print('          "AGNES_API_KEY", "您的_API_KEY", "User")')
        print()
        print("步骤 3: 验证配置")
        print("   agnes key status")
        print()
        print("=" * 50)
    
    def generate_video(self, prompt, num_frames=121, frame_rate=24, images=None, mode='normal', auto_check=True):
        """
        生成视频
        
        Args:
            prompt: 视频描述
            num_frames: 帧数
            frame_rate: 帧率
            images: 关键帧图片列表
            mode: 模式
            auto_check: 是否自动查询状态
        
        Returns:
            dict: 完整的生成结果
        """
        # 检查系统状态
        if not self.status['ready']:
            print("[X] 系统未就绪，无法生成视频")
            for issue in self.status['issues']:
                if issue['type'] == 'missing_api_key':
                    self.guide_api_key_setup()
                    return {'success': False, 'error': 'API Key 未配置'}
            
            return {'success': False, 'error': '系统未就绪'}
        
        print("[*] 开始生成视频...")
        print(f"   描述: {prompt}")
        print(f"   帧数: {num_frames}")
        print(f"   帧率: {frame_rate} fps")
        print(f"   时长: {calculate_duration(num_frames, frame_rate):.2f} 秒")
        print()
        
        # 验证帧数（必须是 8n+1 且 <= 441）
        if not validate_num_frames(num_frames):
            valid_values = [1, 9, 17, 25, 33, 41, 49, 57, 65, 73, 81, 89, 97, 105, 113, 121, 129, 137, 145, 153, 161, 169, 177, 185, 193, 201, 209, 217, 225, 233, 241, 249, 257, 265, 273, 281, 289, 297, 305, 313, 321, 329, 337, 345, 353, 361, 369, 377, 385, 393, 401, 409, 417, 425, 433, 441]
            closest = min([v for v in valid_values if v >= num_frames], default=121)
            print(f"[!] 帧数不符合要求（必须是 8 的倍数 + 1，且 <= 441）")
            print(f"   当前: {num_frames}")
            print(f"   建议: {closest}")
            return {
                'success': False,
                'error': f'帧数不符合要求',
                'valid_values': valid_values,
                'suggested_value': closest
            }
        
        # 创建视频任务
        result = generate_video(
            prompt=prompt,
            num_frames=num_frames,
            frame_rate=frame_rate,
            images=images,
            mode=mode
        )
        
        if not result.get('success'):
            print("[X] 视频生成任务创建失败")
            print(f"   错误: {result.get('error', 'Unknown error')}")
            return result
        
        print("[+] 视频生成任务已提交")
        print(f"   Video ID: {result.get('video_id', 'N/A')}")
        print(f"   Task ID: {result.get('task_id', 'N/A')}")
        print()
        
        # 自动查询状态
        if auto_check and result.get('video_id'):
            print("[*] 等待视频生成...")
            print("   (每 5 秒查询一次状态)")
            print()
            
            status_result = check_status(
                result['video_id'],
                poll_interval=5,
                max_attempts=120  # 最多等待 10 分钟
            )
            
            # 合并结果
            result['status'] = status_result.get('status')
            result['video_url'] = status_result.get('video_url')
            result['status_history'] = status_result.get('history')
            result['final_result'] = status_result
        
        return result
    
    def check_status(self, video_id, poll=False, interval=5, max_attempts=60):
        """
        查询视频生成状态
        
        Args:
            video_id: 视频 ID
            poll: 是否轮询
            interval: 轮询间隔
            max_attempts: 最大查询次数
        
        Returns:
            dict: 状态查询结果
        """
        if not video_id:
            return {'success': False, 'error': '未提供 video_id'}
        
        if poll:
            return check_status(video_id, poll_interval=interval, max_attempts=max_attempts)
        else:
            return query_single_status(video_id)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Agnes Video - AI 视频生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 检查系统状态
  python video_manager.py check

  # 引导 API Key 配置
  python video_manager.py guide

  # 生成 5 秒视频
  python video_manager.py generate --prompt "一只猫在海滩上散步" --num-frames 121 --frame-rate 24

  # 生成 10 秒视频
  python video_manager.py generate --prompt "日落时分的海边风景" --num-frames 241 --frame-rate 24

  # 查询视频状态
  python video_manager.py status <video_id>

  # 持续查询状态直到完成
  python video_manager.py status <video_id> --poll --interval 5
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # check 命令
    subparsers.add_parser('check', help='检查系统状态和 API Key 配置')
    
    # guide 命令
    subparsers.add_parser('guide', help='引导配置 API Key')
    
    # generate 命令
    gen_parser = subparsers.add_parser('generate', help='生成视频')
    gen_parser.add_argument('--prompt', '-p', required=True, help='视频描述')
    gen_parser.add_argument('--num-frames', '-n', type=int, default=121, help='帧数（必须是 16 的倍数 + 1）')
    gen_parser.add_argument('--frame-rate', '-f', type=int, default=24, help='帧率')
    gen_parser.add_argument('--image', '-i', action='append', help='关键帧图片')
    gen_parser.add_argument('--mode', '-m', default='normal', choices=['normal', 'keyframes'], help='模式')
    gen_parser.add_argument('--no-auto-check', action='store_true', help='不自动查询状态')
    
    # status 命令
    status_parser = subparsers.add_parser('status', help='查询视频状态')
    status_parser.add_argument('video_id', help='视频 ID 或任务 ID')
    status_parser.add_argument('--poll', '-p', action='store_true', help='持续轮询')
    status_parser.add_argument('--interval', '-i', type=int, default=5, help='轮询间隔')
    status_parser.add_argument('--max-attempts', '-m', type=int, default=60, help='最大查询次数')
    
    args = parser.parse_args()
    
    # 创建管理器
    manager = AgnesVideoManager()
    
    # 执行命令
    if args.command == 'check':
        manager.check_api_key()
        return 0 if manager.status['ready'] else 1
    
    elif args.command == 'guide':
        manager.guide_api_key_setup()
        return 0
    
    elif args.command == 'generate':
        result = manager.generate_video(
            prompt=args.prompt,
            num_frames=args.num_frames,
            frame_rate=args.frame_rate,
            images=args.image,
            mode=args.mode,
            auto_check=not args.no_auto_check
        )
        
        print("\n[>] 完整结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        return 0 if result.get('success') else 1
    
    elif args.command == 'status':
        result = manager.check_status(
            video_id=args.video_id,
            poll=args.poll,
            interval=args.interval,
            max_attempts=args.max_attempts
        )
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if result.get('status') == 'completed':
            return 0
        elif result.get('status') == 'failed':
            return 2
        else:
            return 1
    
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
