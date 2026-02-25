#!/usr/bin/env python3
"""
题库系统项目验证脚本

用于验证项目修改后仍然正常工作。
每次修改后运行此脚本进行自验证。
"""

import os
import sys
import subprocess
import time
import json
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 颜色定义
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def print_info(msg: str):
    """打印信息"""
    print(f"{BLUE}ℹ️  {msg}{NC}")


def print_success(msg: str):
    """打印成功"""
    print(f"{GREEN}✅ {msg}{NC}")


def print_warning(msg: str):
    """打印警告"""
    print(f"{YELLOW}⚠️  {msg}{NC}")


def print_error(msg: str):
    """打印错误"""
    print(f"{RED}❌ {msg}{NC}")


class ProjectValidator:
    """项目验证器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = []
    
    def run_test(self, name: str, test_func) -> bool:
        """运行单个测试"""
        print_info(f"测试: {name}")
        try:
            result = test_func()
            if result:
                print_success(f"{name} - 通过")
                self.results.append((name, True, None))
                return True
            else:
                print_error(f"{name} - 失败")
                self.results.append((name, False, "测试返回False"))
                return False
        except Exception as e:
            print_error(f"{name} - 异常: {e}")
            self.results.append((name, False, str(e)))
            return False
    
    def test_project_structure(self) -> bool:
        """测试项目结构"""
        required_dirs = [
            "config",
            "core",
            "core/database",
            "data",
            "mcp_server",
            "web",
            "wechat",
            "shared",
            "test",
        ]
        
        required_files = [
            "README.md",
            "run.sh",
            "start.py",
            "config/requirements.txt",
            "config/pyproject.toml",
            "web/main.py",
            "web/config.py",
            "mcp_server/server.py",
            "mcp_server/config.py",
            "wechat/server.py",
            "wechat/config.py",
            "shared/config.py",
        ]
        
        # 检查目录
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                print_error(f"目录不存在: {dir_path}")
                return False
        
        # 检查文件
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                print_error(f"文件不存在: {file_path}")
                return False
        
        return True
    
    def test_python_imports(self) -> bool:
        """测试Python导入"""
        test_cases = [
            ("shared.config", "config"),
            ("core.database.connection", "db"),
            ("core.database.migrations", "create_tables"),
            ("core.models", "QuestionCreate"),
            ("core.services", "QuestionService"),
            ("web.main", "app"),
            ("web.config", "settings"),
            ("mcp_server.server", "app"),
            ("mcp_server.config", "settings"),
            ("wechat.server", "app"),
            ("wechat.config", "settings"),
        ]
        
        # 添加项目根目录到Python路径
        sys.path.insert(0, str(self.project_root))
        
        for module_name, attr_name in test_cases:
            try:
                module = __import__(module_name, fromlist=[attr_name])
                if hasattr(module, attr_name):
                    print_info(f"  导入成功: {module_name}.{attr_name}")
                else:
                    print_error(f"  属性不存在: {module_name}.{attr_name}")
                    return False
            except ImportError as e:
                print_error(f"  导入失败: {module_name} - {e}")
                return False
        
        return True
    
    def test_run_script(self) -> bool:
        """测试运行脚本"""
        run_script = self.project_root / "run.sh"
        
        # 检查脚本是否存在且可执行
        if not run_script.exists():
            print_error("run.sh不存在")
            return False
        
        if not os.access(run_script, os.X_OK):
            print_error("run.sh不可执行")
            return False
        
        # 测试帮助命令
        try:
            result = subprocess.run(
                [str(run_script), "help"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5
            )
            if result.returncode == 0:
                print_info("  run.sh help命令正常")
                return True
            else:
                print_error(f"  run.sh help命令失败: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print_error("  run.sh help命令超时")
            return False
        except Exception as e:
            print_error(f"  run.sh help命令异常: {e}")
            return False
    
    def test_web_service(self) -> bool:
        """测试Web服务"""
        # 先停止可能存在的服务
        self._stop_services()
        
        # 启动Web服务
        try:
            process = subprocess.Popen(
                ["./run.sh", "web"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务启动
            time.sleep(5)
            
            # 测试健康检查
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy" and data.get("service") == "web":
                        print_info("  Web服务健康检查通过")
                        
                        # 测试根路径
                        response = requests.get("http://localhost:8000/", timeout=5)
                        if response.status_code == 200:
                            print_info("  Web服务根路径访问正常")
                            
                            # 停止服务
                            process.terminate()
                            process.wait(timeout=5)
                            return True
            except requests.RequestException as e:
                print_error(f"  Web服务请求失败: {e}")
            
            # 停止服务
            process.terminate()
            process.wait(timeout=5)
            return False
            
        except Exception as e:
            print_error(f"  Web服务测试异常: {e}")
            return False
    
    def test_mcp_service(self) -> bool:
        """测试MCP服务"""
        # 先停止可能存在的服务
        self._stop_services()
        
        # 获取Python命令
        python_cmd = self._get_python_command()
        if not python_cmd:
            print_error("  未找到Python命令")
            return False
        
        # 启动MCP服务
        try:
            process = subprocess.Popen(
                [python_cmd, "-m", "uvicorn", "mcp_server.server:app", "--host", "0.0.0.0", "--port", "8001"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务启动
            time.sleep(3)
            
            # 测试健康检查
            try:
                response = requests.get("http://localhost:8001/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy" and data.get("service") == "mcp":
                        print_info("  MCP服务健康检查通过")
                        
                        # 停止服务
                        process.terminate()
                        process.wait(timeout=5)
                        return True
            except requests.RequestException as e:
                print_error(f"  MCP服务请求失败: {e}")
            
            # 停止服务
            process.terminate()
            process.wait(timeout=5)
            return False
            
        except Exception as e:
            print_error(f"  MCP服务测试异常: {e}")
            return False
    
    def test_wechat_service(self) -> bool:
        """测试微信服务"""
        # 先停止可能存在的服务
        self._stop_services()
        
        # 获取Python命令
        python_cmd = self._get_python_command()
        if not python_cmd:
            print_error("  未找到Python命令")
            return False
        
        # 启动微信服务
        try:
            process = subprocess.Popen(
                [python_cmd, "-m", "uvicorn", "wechat.server:app", "--host", "0.0.0.0", "--port", "8002"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务启动
            time.sleep(3)
            
            # 测试健康检查
            try:
                response = requests.get("http://localhost:8002/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy" and data.get("service") == "wechat":
                        print_info("  微信服务健康检查通过")
                        
                        # 停止服务
                        process.terminate()
                        process.wait(timeout=5)
                        return True
            except requests.RequestException as e:
                print_error(f"  微信服务请求失败: {e}")
            
            # 停止服务
            process.terminate()
            process.wait(timeout=5)
            return False
            
        except Exception as e:
            print_error(f"  微信服务测试异常: {e}")
            return False
    
    def test_database(self) -> bool:
        """测试数据库"""
        try:
            # 导入数据库模块
            sys.path.insert(0, str(self.project_root))
            from core.database.migrations import create_tables
            
            # 确保数据目录存在
            data_dir = self.project_root / "data"
            data_dir.mkdir(exist_ok=True)
            
            # 创建表
            create_tables()
            print_info("  数据库表创建成功")
            
            # 检查数据库文件
            db_file = data_dir / "question_bank.db"
            if db_file.exists():
                print_info(f"  数据库文件存在: {db_file}")
                return True
            else:
                print_error("  数据库文件不存在")
                return False
                
        except Exception as e:
            print_error(f"  数据库测试异常: {e}")
            return False
    
    def _get_python_command(self) -> str:
        """获取Python命令"""
        # 检查python3
        try:
            subprocess.run(["python3", "--version"], capture_output=True, check=True)
            return "python3"
        except:
            pass
        
        # 检查python
        try:
            subprocess.run(["python", "--version"], capture_output=True, check=True)
            return "python"
        except:
            pass
        
        return None
    
    def _stop_services(self):
        """停止所有服务"""
        try:
            # 使用run.sh停止服务
            subprocess.run(
                ["./run.sh", "stop"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            time.sleep(2)
        except:
            pass  # 忽略停止失败
    
    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print_info("🚀 开始项目验证")
        print_info(f"项目根目录: {self.project_root}")
        print()
        
        tests = [
            ("项目结构", self.test_project_structure),
            ("Python导入", self.test_python_imports),
            ("运行脚本", self.test_run_script),
            ("数据库", self.test_database),
            ("Web服务", self.test_web_service),
            ("MCP服务", self.test_mcp_service),
            ("微信服务", self.test_wechat_service),
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            if not self.run_test(test_name, test_func):
                all_passed = False
        
        print()
        print_info("📊 测试结果汇总")
        print("-" * 50)
        
        passed_count = 0
        failed_count = 0
        
        for name, passed, error in self.results:
            if passed:
                print_success(f"{name}")
                passed_count += 1
            else:
                print_error(f"{name}: {error}")
                failed_count += 1
        
        print("-" * 50)
        
        if all_passed:
            print_success(f"✅ 所有测试通过 ({passed_count}/{len(tests)})")
            return True
        else:
            print_error(f"❌ 测试失败 ({passed_count}通过, {failed_count}失败)")
            return False


def main():
    """主函数"""
    validator = ProjectValidator()
    
    if len(sys.argv) > 1:
        # 运行特定测试
        test_name = sys.argv[1]
        if test_name == "structure":
            result = validator.test_project_structure()
        elif test_name == "imports":
            result = validator.test_python_imports()
        elif test_name == "script":
            result = validator.test_run_script()
        elif test_name == "database":
            result = validator.test_database()
        elif test_name == "web":
            result = validator.test_web_service()
        elif test_name == "mcp":
            result = validator.test_mcp_service()
        elif test_name == "wechat":
            result = validator.test_wechat_service()
        else:
            print_error(f"未知测试: {test_name}")
            print_info("可用测试: structure, imports, script, database, web, mcp, wechat")
            sys.exit(1)
        
        sys.exit(0 if result else 1)
    else:
        # 运行所有测试
        result = validator.run_all_tests()
        sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()