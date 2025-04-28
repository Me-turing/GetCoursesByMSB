#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import os
from typing import Dict, Any, List, Optional
import time

class MCARequest:
    def __init__(self):
        self.session = requests.Session()
        self.data_dir = "data"
        self.ensure_data_dir()
        self.base_url = "https://gateway.mashibing.com"
        self.current_outline = None
        
    def ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def fetch_course_packages(self) -> Dict[str, Any]:
        """获取课程包信息"""
        url = f"{self.base_url}/edu-course/coursePackage/homePage"
        params = {
            "length": 999,
            "pageIndex": 1
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        result = response.json()
        
        # 不再保存到文件
        return result
    
    def fetch_course_package_versions(self, course_package_id: str) -> Dict[str, Any]:
        """获取课程包版本列表"""
        url = f"{self.base_url}/edu-course/pc/coursePackageVersion"
        params = {
            "coursePackageId": course_package_id
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        result = response.json()
        
        # 不再保存到文件
        return result
    
    def fetch_course_outline(self, outline_id=None):
        """获取课程大纲"""
        url = f"{self.base_url}/api/course/outline/get"
        
        if not outline_id:
            # 获取默认大纲
            request_data = {
                "clientTime": int(time.time() * 1000)
            }
        else:
            # 获取特定大纲
            request_data = {
                "outlineId": outline_id,
                "clientTime": int(time.time() * 1000)
            }
        
        response = self.session.post(url, json=request_data)
        if response.status_code != 200:
            print(f"获取课程大纲失败: HTTP {response.status_code}")
            return None
        
        data = response.json()
        if data.get('code') != 0:
            print(f"获取课程大纲失败: {data.get('message', '未知错误')}")
            return None
        
        # 提取大纲数据
        data = data.get('data', {})
        
        # 首先尝试获取stageList（阶段列表）
        stage_list = data.get('stageList', [])
        if stage_list:
            print(f"找到课程阶段列表，共{len(stage_list)}个阶段")
            self.display_course_outline(stage_list)
            # 保存完整大纲数据供后续使用
            self.current_outline = stage_list
            return stage_list
        
        # 如果没有stageList，尝试获取courseItemList（课程列表）
        course_list = data.get('courseItemList', [])
        if course_list:
            print(f"找到课程列表，共{len(course_list)}个课程")
            self.display_course_outline(course_list)
            # 保存完整大纲数据供后续使用
            self.current_outline = course_list
            return course_list
        
        # 如果上述都没有，尝试获取嵌套结构的大纲
        outline = data.get('outline', {})
        children = outline.get('children', [])
        if children:
            print("找到嵌套结构大纲")
            self.display_course_outline(children)
            # 保存完整大纲数据供后续使用
            self.current_outline = children
            return children
        
        print("未找到课程大纲数据")
        return None
    
    def load_course_packages(self) -> Dict[str, Any]:
        """获取课程包信息，不再从文件加载"""
        print("获取课程包数据...")
        return self.fetch_course_packages()
    
    def load_course_package_versions(self, course_package_id: str) -> Dict[str, Any]:
        """获取课程包版本列表，不再从文件加载"""
        print(f"获取课程包ID {course_package_id} 的版本列表...")
        return self.fetch_course_package_versions(course_package_id)
    
    def load_course_outline(self, course_id: str, package_version_id: str) -> Dict[str, Any]:
        """加载已保存的课程大纲"""
        file_path = os.path.join(self.data_dir, f"course_outline_{course_id}_{package_version_id}.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}，请先获取课程大纲数据")
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_course_list(self) -> List[Dict[str, Any]]:
        """获取课程列表"""
        data = self.load_course_packages()
        
        # 打印JSON的顶层结构，以便了解数据格式
        print("\n数据结构分析:")
        print("顶层键:", list(data.keys()))
        
        if 'data' in data:
            print("data字段类型:", type(data['data']).__name__)
            data_obj = data['data']
            
            if isinstance(data_obj, dict):
                print("data字段的键:", list(data_obj.keys()))
                
                # 检查data.content字段
                if 'content' in data_obj:
                    print("content字段类型:", type(data_obj['content']).__name__)
                    if isinstance(data_obj['content'], list):
                        print("content长度:", len(data_obj['content']))
                        if data_obj['content'] and isinstance(data_obj['content'][0], dict):
                            print("第一个content项的键:", list(data_obj['content'][0].keys()))
                            # 如果content存在且是列表，返回它
                            return data_obj['content']
                
                if 'list' in data_obj:
                    print("list字段类型:", type(data_obj['list']).__name__)
                    print("list长度:", len(data_obj['list']) if isinstance(data_obj['list'], list) else "不是列表")
                    
                    if isinstance(data_obj['list'], list) and len(data_obj['list']) > 0:
                        print("第一个列表项的键:", list(data_obj['list'][0].keys()) if isinstance(data_obj['list'][0], dict) else "不是字典")
                        return data_obj['list']
            
            elif isinstance(data_obj, list):
                print("data是列表，长度:", len(data_obj))
                if data_obj and isinstance(data_obj[0], dict):
                    print("第一个列表项的键:", list(data_obj[0].keys()))
                    return data_obj
            
            # 优先检查content字段
            if isinstance(data_obj, dict):
                if 'content' in data_obj and isinstance(data_obj['content'], list):
                    return data_obj['content']
                elif 'list' in data_obj and isinstance(data_obj['list'], list):
                    return data_obj['list']
            elif isinstance(data_obj, list):
                return data_obj
        
        # 如果找不到标准路径，尝试在JSON中搜索可能的课程列表
        print("\n尝试查找可能包含课程的列表...")
        for key, value in data.items():
            if isinstance(value, list) and value and isinstance(value[0], dict) and 'title' in value[0]:
                print(f"找到可能的列表在键 '{key}'，长度: {len(value)}")
                return value
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, list) and subvalue and isinstance(subvalue[0], dict) and 'title' in subvalue[0]:
                        print(f"找到可能的列表在键 '{key}.{subkey}'，长度: {len(subvalue)}")
                        return subvalue
        
        return []
    
    def get_course_package_versions(self, course_package_id: str) -> List[Dict[str, Any]]:
        """获取课程包版本列表"""
        print(f"获取课程包ID {course_package_id} 的版本列表...")
        data = self.fetch_course_package_versions(course_package_id)

        if 'data' in data and isinstance(data['data'], list):
            version_list = data['data']
            return version_list
        
        return []
    
    def get_course_outline(self, outline_id=None):
        """获取课程大纲"""
        url = f"{self.base_url}/api/course/outline/get"
        
        if not outline_id:
            # 获取默认大纲
            request_data = {
                "clientTime": int(time.time() * 1000)
            }
        else:
            # 获取特定大纲
            request_data = {
                "outlineId": outline_id,
                "clientTime": int(time.time() * 1000)
            }
        
        response = self.session.post(url, json=request_data)
        if response.status_code != 200:
            print(f"获取课程大纲失败: HTTP {response.status_code}")
            return None
        
        data = response.json()
        if data.get('code') != 0:
            print(f"获取课程大纲失败: {data.get('message', '未知错误')}")
            return None
        
        # 提取大纲数据
        data = data.get('data', {})
        
        # 首先尝试获取stageList（阶段列表）
        stage_list = data.get('stageList', [])
        if stage_list:
            print(f"找到课程阶段列表，共{len(stage_list)}个阶段")
            self.display_course_outline(stage_list)
            # 保存完整大纲数据供后续使用
            self.current_outline = stage_list
            return stage_list
        
        # 如果没有stageList，尝试获取courseItemList（课程列表）
        course_list = data.get('courseItemList', [])
        if course_list:
            print(f"找到课程列表，共{len(course_list)}个课程")
            self.display_course_outline(course_list)
            # 保存完整大纲数据供后续使用
            self.current_outline = course_list
            return course_list
        
        # 如果上述都没有，尝试获取嵌套结构的大纲
        outline = data.get('outline', {})
        children = outline.get('children', [])
        if children:
            print("找到嵌套结构大纲")
            self.display_course_outline(children)
            # 保存完整大纲数据供后续使用
            self.current_outline = children
            return children
        
        print("未找到课程大纲数据")
        return None
    
    def check_other_course_fields(self, data_obj: Dict[str, Any]):
        """检查数据中其他可能包含课程信息的字段"""
        print("\n尝试找出其他可能包含课程信息的字段...")
        
        # 检查基本课程信息
        if 'title' in data_obj:
            print(f"课程标题: {data_obj.get('title')}")
        if 'description' in data_obj:
            desc = data_obj.get('description', '')
            print(f"课程描述: {desc[:100]}..." if len(desc) > 100 else f"课程描述: {desc}")
        
        # 检查课程统计信息
        if 'courseCount' in data_obj:
            print(f"课程总数: {data_obj.get('courseCount')}")
        if 'sectionCount' in data_obj:
            print(f"章节总数: {data_obj.get('sectionCount')}")
        if 'totalVideoDuration' in data_obj:
            duration = data_obj.get('totalVideoDuration', 0)
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            print(f"总视频时长: {hours}小时{minutes}分钟{seconds}秒")
        
        # 检查课程详情
        if 'courseDetail' in data_obj and data_obj['courseDetail']:
            print("找到课程详情内容，长度:", len(data_obj['courseDetail']))
            with open(os.path.join(self.data_dir, "course_detail.md"), "w", encoding="utf-8") as f:
                f.write(data_obj['courseDetail'])
            print("已将课程详情内容保存为Markdown文件: course_detail.md")
    
    def print_json_result(self, data: Dict[str, Any]):
        """打印JSON结果的基本信息"""
        print(f"请求成功，结果状态码: {data.get('code')}")
        print(f"结果消息: {data.get('msg')}")
        if 'data' in data:
            data_obj = data.get('data', {})
            if isinstance(data_obj, dict):
                if 'totalElements' in data_obj:
                    print(f"总数据条数: {data_obj.get('totalElements')}")
                if 'content' in data_obj and isinstance(data_obj.get('content'), list):
                    print(f"返回列表项数: {len(data_obj.get('content'))}")
    
    def show_course_selection(self) -> Optional[Dict[str, Any]]:
        """显示课程选择界面"""
        courses = self.get_course_list()
        
        if not courses:
            print("没有找到课程数据")
            # 另一种可能：data字段中可能没有列表，而是单个对象
            data = self.load_course_packages()
            if 'data' in data and isinstance(data['data'], dict):
                print("\n检查data字段是否为单个课程...")
                if 'title' in data['data']:
                    print(f"找到单个课程: {data['data'].get('title')}")
                    return [data['data']]
            return None
        
        print("\n" + "="*80)
        print("课程列表".center(78))
        print("="*80)
        
        for i, course in enumerate(courses, 1):
            # 优先使用title字段获取课程名称
            title = course.get('title', '未知名称')
            if not title:  # 如果title为空，尝试其他可能的字段名
                title = course.get('name', course.get('packageName', course.get('courseName', '未知名称')))
            price = course.get('price', course.get('actualPrice', 0))
            description = course.get('description', '无描述')
            
            # 格式化输出，限制描述长度以避免太长
            max_desc_length = 50
            if len(description) > max_desc_length:
                description = description[:max_desc_length] + "..."
            
            print(f"{i:3}. {title} (价格: ¥{price})")
            print(f"    描述: {description}")
            print(f"    {'--'*39}")
        
        print("="*80)
        print("0. 退出")
        print("="*80)
        
        while True:
            try:
                choice = int(input("\n请选择课程编号: "))
                if choice == 0:
                    return None
                if 1 <= choice <= len(courses):
                    return courses[choice-1]
                print(f"错误: 请输入0-{len(courses)}之间的数字")
            except ValueError:
                print("错误: 请输入数字")
    
    def show_course_package_versions(self, course_package_id: str) -> Optional[Dict[str, Any]]:
        """显示课程包版本选择界面"""
        versions = self.get_course_package_versions(course_package_id)
        
        if not versions:
            print(f"课程包ID {course_package_id} 没有找到版本列表")
            return None
        
        print("\n" + "="*80)
        print(f"课程包 {course_package_id} 的版本列表".center(78))
        print("="*80)
        
        for i, version in enumerate(versions, 1):
            version_id = version.get('id', '未知')
            name = version.get('name', '未知名称')
            enabled = version.get('enabled', 0)
            status = "启用" if enabled == 1 else "禁用"
            
            print(f"{i:3}. {name} (ID: {version_id}, 状态: {status})")
        
        print("="*80)
        print("0. 退出")
        print("="*80)
        
        while True:
            try:
                choice = int(input("\n请选择版本编号: "))
                if choice == 0:
                    return None
                if 1 <= choice <= len(versions):
                    return versions[choice-1]
                print(f"错误: 请输入0-{len(versions)}之间的数字")
            except ValueError:
                print("错误: 请输入数字")
    
    def display_course_outline(self, outline_list: List[Dict[str, Any]], level: int = 0):
        """递归显示课程大纲"""
        if not outline_list:
            print("  " * level + "无大纲内容")
            return
        
        # 检查是否为stageList结构
        if level == 0 and outline_list and isinstance(outline_list, list) and isinstance(outline_list[0], dict) and 'courseList' in outline_list[0]:
            print("\n课程阶段列表:")
            for i, stage in enumerate(outline_list, 1):
                stage_id = stage.get('id', '未知')
                stage_title = stage.get('title', '未知名称')
                stage_desc = stage.get('description', '无描述')
                
                print(f"{i}. {stage_title} (ID: {stage_id})")
                if stage_desc and stage_desc != stage_title:
                    print(f"   描述: {stage_desc}")
                
                # 显示阶段中的课程列表
                course_list = stage.get('courseList', [])
                if course_list:
                    print("   包含课程:")
                    for j, course in enumerate(course_list, 1):
                        course_id = course.get('id', '未知')
                        course_name = course.get('courseName', '未知名称')
                        duration = course.get('durationTotal', 0)
                        
                        # 确保duration不为None
                        if duration is None:
                            duration = 0
                            duration_str = "未知"
                        else:
                            # 将秒转换为小时:分钟:秒
                            hours = duration // 3600
                            minutes = (duration % 3600) // 60
                            seconds = duration % 60
                            duration_str = f"{hours}小时{minutes}分钟{seconds}秒"
                        
                        section_count = course.get('sectionCount', 0)
                        
                        print(f"     {j}. {course_name} (ID: {course_id})")
                        print(f"        时长: {duration_str}, 章节数: {section_count}")
                else:
                    print("   无课程")
                
                print(f"   {'--'*30}")
            return
        
        # 检查是否为courseItemList结构
        if level == 0 and outline_list and isinstance(outline_list, list) and isinstance(outline_list[0], dict) and ('courseNo' in outline_list[0] or 'courseName' in outline_list[0] or 'title' in outline_list[0]):
            print("\n课程列表:")
            for i, item in enumerate(outline_list, 1):
                course_no = item.get('courseNo', item.get('id', '未知'))
                course_name = item.get('courseName', item.get('title', '未知名称'))
                duration = item.get('durationTotal', 0)
                
                # 确保duration不为None
                if duration is None:
                    duration = 0
                    duration_str = "未知"
                else:
                    # 将秒转换为小时:分钟:秒
                    hours = duration // 3600
                    minutes = (duration % 3600) // 60
                    seconds = duration % 60
                    duration_str = f"{hours}小时{minutes}分钟{seconds}秒"
                
                section_count = item.get('sectionCount', 0)
                
                print(f"{i:2}. {course_name}")
                print(f"   课程编号: {course_no}")
                if duration:
                    print(f"   总时长: {duration_str}")
                if section_count:
                    print(f"   章节数: {section_count}")
                print(f"   {'--'*30}")
            return
        
        # 原有的递归显示逻辑，用于处理嵌套结构
        for i, item in enumerate(outline_list, 1):
            # 获取项目信息
            title = item.get('title', item.get('name', '未知名称'))
            item_id = item.get('id', '未知')
            item_type = item.get('itemType', item.get('type', '未知'))
            
            # 根据层级缩进，并显示条目编号和名称
            indent = "  " * level
            print(f"{indent}{i}. [{item_type}] {title} (ID: {item_id})")
            
            # 递归处理子项目
            children = item.get('children', [])
            if children:
                self.display_course_outline(children, level + 1)
    
    def save_outline_for_download(self, outline_list: List[Dict[str, Any]], course_id: str, package_version_id: str):
        """保存大纲信息用于后续下载"""
        # 这个函数不再生成文件，只作为处理过程的一部分
        flat_items = []
        
        # 检查是否为courseItemList结构
        if outline_list and 'courseNo' in outline_list[0]:
            for item in outline_list:
                course_no = item.get('courseNo', '未知')
                course_name = item.get('courseName', '未知名称')
                duration = item.get('durationTotal', 0)
                section_count = item.get('sectionCount', 0)
                
                # 构建课程项
                course_data = {
                    'id': course_no,
                    'title': course_name,
                    'type': 'course',
                    'duration': duration,
                    'section_count': section_count
                }
                flat_items.append(course_data)
            
            return
        
        # 原有的递归提取逻辑，用于处理嵌套结构
        def extract_items(items, parent_path=""):
            for i, item in enumerate(items, 1):
                title = item.get('title', item.get('name', '未知名称'))
                item_id = item.get('id', '未知')
                item_type = item.get('itemType', item.get('type', '未知'))
                current_path = f"{parent_path}{i}."
                
                # 保存当前项
                item_data = {
                    'id': item_id,
                    'title': title,
                    'type': item_type,
                    'path': current_path,
                    'parent_path': parent_path
                }
                flat_items.append(item_data)
                
                # 递归处理子项
                children = item.get('children', [])
                if children:
                    extract_items(children, current_path)
        
        extract_items(outline_list)
    
    def display_course_details(self, course: Dict[str, Any]):
        """显示课程详细信息"""
        if not course:
            return
        
        print("\n" + "="*80)
        print("课程详情".center(78))
        print("="*80)
        
        # 优先使用title字段获取课程名称
        title = course.get('title', '未知名称')
        if not title:
            title = course.get('name', course.get('packageName', course.get('courseName', '未知名称')))
        
        course_id = course.get('id', '未知')
        price = course.get('price', 0)
        description = course.get('description', '无描述')
        
        # 显示基本信息
        print(f"名称: {title}")
        print(f"ID: {course_id}")
        print(f"价格: ¥{price}")
        print(f"描述: {description}")
        
        # 显示其他重要信息
        study_count = course.get('studyCount')
        if study_count is not None:
            print(f"学习人数: {study_count}")
        
        section_count = course.get('sectionCount')
        if section_count:
            print(f"章节数: {section_count}")
        
        course_count = course.get('courseCount')
        if course_count:
            print(f"课程数: {course_count}")
        
        video_duration = course.get('totalVideoDuration')
        if video_duration:
            # 将视频时长（秒）转换为小时:分钟:秒格式
            hours = video_duration // 3600
            minutes = (video_duration % 3600) // 60
            seconds = video_duration % 60
            print(f"总视频时长: {hours}小时{minutes}分钟{seconds}秒")
        
        level = course.get('level')
        if level:
            print(f"等级: {level}")
        
        degree = course.get('degree')
        if degree:
            print(f"难度: {degree}")
        
        # 显示子课程信息
        child_courses = course.get('pcSystemCourseChildSimpleVos', [])
        if child_courses:
            print("\n包含的子课程:")
            for i, child in enumerate(child_courses, 1):
                child_title = child.get('title', '未知')
                child_desc = child.get('description', '无描述')
                print(f"  {i}. {child_title}")
                print(f"     {child_desc}")
        
        print("\n其他信息:")
        # 排除已显示的字段
        excluded_keys = ['id', 'title', 'price', 'description', 'studyCount', 
                         'sectionCount', 'courseCount', 'totalVideoDuration',
                         'level', 'degree', 'pcSystemCourseChildSimpleVos',
                         'name', 'packageName', 'courseName']
        
        for key, value in course.items():
            if key not in excluded_keys:
                if isinstance(value, (str, int, float, bool)) and value:
                    print(f"  {key}: {value}")
        
        print("="*80)
    
    def display_course_package_version(self, version: Dict[str, Any]):
        """显示课程包版本详细信息"""
        if not version:
            return
        
        print("\n" + "="*80)
        print("课程包版本详情".center(78))
        print("="*80)
        
        # 显示基本信息
        print(f"ID: {version.get('id', '未知')}")
        print(f"课程包ID: {version.get('coursePackageId', '未知')}")
        print(f"名称: {version.get('name', '未知名称')}")
        enabled = version.get('enabled', 0)
        status = "启用" if enabled == 1 else "禁用"
        print(f"状态: {status}")
        
        # 显示其他信息
        for key, value in version.items():
            if key not in ['id', 'coursePackageId', 'name', 'enabled']:
                if isinstance(value, (str, int, float, bool)) and value:
                    print(f"{key}: {value}")
        
        print("="*80)

    def extract_course_structure(self, outline_data) -> List[Dict[str, Any]]:
        """提取课程结构，生成扁平化目录
        
        Args:
            outline_data: 课程大纲数据
            
        Returns:
            List[Dict[str, Any]]: 扁平化的课程结构
        """
        result = []
        
        def process_item(item, path=None, level=0, parent_info=None):
            if path is None:
                path = []
            
            # 复制当前路径并添加当前项
            current_path = path.copy()
            
            # 获取基本信息
            item_id = item.get('id', '')
            title = item.get('title', item.get('name', '未知'))
            item_type = item.get('itemType', item.get('type', ''))
            
            # 构建当前项目的完整路径
            if title:
                current_path.append(title)
            
            # 处理视频类型
            is_video = False
            video_url = None
            duration = 0
            
            if item_type in ['Video', 'video']:
                is_video = True
                resources = item.get('resources', [])
                for resource in resources:
                    if resource.get('resourceType') == 'video':
                        video_url = resource.get('url', '')
                        break
                
                duration = item.get('duration', 0)
            
            # 创建当前项的记录
            item_info = {
                'id': item_id,
                'title': title,
                'type': item_type,
                'level': level,
                'path': ' > '.join(current_path),
                'is_video': is_video,
                'video_url': video_url,
                'duration': duration,
                'parent_info': parent_info
            }
            
            # 添加到结果列表
            result.append(item_info)
            
            # 处理子项目
            children = item.get('children', [])
            for child in children:
                process_item(child, current_path, level + 1, item_info)
        
        # 处理根级别的项目
        if isinstance(outline_data, dict):
            # 单个课程大纲
            process_item(outline_data)
        elif isinstance(outline_data, list):
            # 课程列表
            for item in outline_data:
                process_item(item)
        
        return result
        
    def generate_course_catalog(self, course_outline, output_file=None):
        """生成课程目录并输出到文件
        
        Args:
            course_outline: 课程大纲数据
            output_file: 输出文件路径，默认为None（不输出到文件）
        """
        flat_structure = self.extract_course_structure(course_outline)
        
        # 准备目录文本
        catalog_lines = []
        catalog_lines.append("# 课程目录\n")
        
        total_duration = 0
        video_count = 0
        
        for item in flat_structure:
            indent = "  " * item['level']
            title = item['title']
            item_type = item['type']
            
            # 为视频添加时长信息
            if item['is_video']:
                duration = item['duration']
                total_duration += duration
                video_count += 1
                
                # 将秒转换为分钟:秒
                minutes = duration // 60
                seconds = duration % 60
                duration_str = f"({minutes:02d}:{seconds:02d})"
                
                line = f"{indent}- [{title}] {duration_str}"
            else:
                line = f"{indent}- **{title}**"
            
            catalog_lines.append(line)
        
        # 添加统计信息
        hours = total_duration // 3600
        minutes = (total_duration % 3600) // 60
        seconds = total_duration % 60
        
        catalog_lines.append(f"\n## 统计信息")
        catalog_lines.append(f"- 视频数量: {video_count}个")
        catalog_lines.append(f"- 总时长: {hours}小时{minutes}分钟{seconds}秒")
        
        # 打印目录
        catalog_text = "\n".join(catalog_lines)
        print(catalog_text)
        
        # 如果指定了输出文件，将目录写入文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(catalog_text)
            print(f"\n目录已保存到: {output_file}")
        
        return catalog_text

    def fetch_course_child(self, course_id: str, package_version_id: str) -> Dict[str, Any]:
        """通过systemCourse/child API获取课程大纲"""
        # 直接将参数拼接到URL中，而不是使用params参数
        url = f"{self.base_url}/edu-course/systemCourse/child/{course_id}?coursePackageVersionId={package_version_id}"
        
        response = self.session.get(url)
        
        if response.status_code != 200:
            print(f"获取课程大纲失败: HTTP {response.status_code}")
            return None
        
        result = response.json()
        
        if result.get('code') != 200:
            print(f"获取课程大纲失败: {result.get('message', '未知错误')}")
            return None
        
        # 不再保存中间文件，直接返回数据
        return result.get('data', {})

    def fetch_course_versions(self, course_id: str) -> Dict[str, Any]:
        """获取课程版本列表及详细信息"""
        url = f"{self.base_url}/edu-course/course/courseversion/allVersionList"
        params = {
            "courseId": course_id,
            "enable": 1
        }
        
        try:
            response = self.session.get(url, params=params)
            
            if response.status_code != 200:
                print(f"警告: 获取课程ID {course_id} 的版本信息失败: HTTP {response.status_code}")
                return None
            
            result = response.json()
            
            if result.get('code') != 200:
                print(f"警告: 获取课程ID {course_id} 的版本信息失败: {result.get('message', '未知错误')}")
                return None
            
            # 返回数据部分，不再保存中间文件
            return result.get('data', [])
        
        except Exception as e:
            print(f"警告: 获取课程ID {course_id} 的版本信息时出错: {e}")
            return None

    def fetch_course_detail(self, course_id: str, course_version_id: str) -> Dict[str, Any]:
        """获取课程详细章节信息"""
        url = f"{self.base_url}/edu-course/courseWeb/{course_id}/pc"
        params = {
            "courseVersionId": course_version_id
        }
        
        try:
            response = self.session.get(url, params=params)
            
            if response.status_code != 200:
                print(f"警告: 获取课程ID {course_id} 的详细章节信息失败: HTTP {response.status_code}")
                return None
            
            result = response.json()
            
            if result.get('code') != 200:
                print(f"警告: 获取课程ID {course_id} 的详细章节信息失败: {result.get('message', '未知错误')}")
                return None
            
            # 返回数据部分
            return result.get('data', {})
        
        except Exception as e:
            print(f"警告: 获取课程ID {course_id} 的详细章节信息时出错: {e}")
            return None

    def enrich_course_outline(self, outline_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """丰富课程大纲，直接添加每个课程的详细描述到已有层级中"""
        if not outline_list or not isinstance(outline_list, list):
            print("警告: 大纲列表为空或格式不正确")
            return outline_list
        
        # 检查输入格式，判断是否为简单列表格式（scratch.json）
        is_simple_format = False
        if outline_list and isinstance(outline_list[0], dict):
            # 检查是否有courseNo字段，这是简单列表格式的特征
            if 'courseNo' in outline_list[0]:
                is_simple_format = True
                print("检测到简单列表格式的课程数据，将使用适配的处理方式...")
        
        # 用于记录章节ID与版本ID的映射关系
        id_mapping = {}
        
        if is_simple_format:
            # 简单列表格式处理方式（scratch.json格式）
            total_courses = len(outline_list)
            processed_courses = 0
            
            print(f"\n开始丰富课程大纲，共 {total_courses} 个课程...")
            
            # 处理每个课程
            for course in outline_list:
                course_id = course.get('courseNo')
                course_name = course.get('courseName', '未知课程')
                
                processed_courses += 1
                progress = processed_courses / total_courses * 100
                print(f"\r处理进度: {processed_courses}/{total_courses} ({progress:.1f}%) - 当前: {course_name}", end="")
                
                if course_id:
                    # 1. 获取课程版本信息
                    versions = self.fetch_course_versions(str(course_id))
                    
                    if versions and len(versions) > 0:
                        # 获取第一个版本的详细信息
                        version = versions[0]
                        version_id = version.get('id')
                        
                        # 添加详细描述到课程对象
                        course['pcDetailDesc'] = version.get('pcDetailDesc', '')
                        course['appDetailDesc'] = version.get('appDetailDesc', '')
                        course['versionId'] = version_id
                        course['versionName'] = version.get('name', '')
                        
                        # 记录章节ID与版本ID的映射关系
                        id_mapping[str(course_id)] = {
                            'versionId': version_id,
                            'courseName': course_name
                        }
                        
                        # 2. 获取课程详细章节信息
                        course_detail = self.fetch_course_detail(str(course_id), str(version_id))
                        if course_detail:
                            # 添加详细章节信息到课程对象
                            course['chapterList'] = course_detail.get('chapterList', [])
                            course['durationSum'] = course_detail.get('durationSum', 0)
                            course['level'] = course_detail.get('level', 0)
                            course['price'] = course_detail.get('price', 0)
                            course['studyCount'] = course_detail.get('studyCount', 0)
                            
                            # 计算总章节数和总小节数
                            chapter_count = len(course['chapterList'])
                            section_count = sum(len(chapter.get('sectionList', [])) for chapter in course['chapterList'])
                            course['totalChapterCount'] = chapter_count
                            course['totalSectionCount'] = section_count
            
            # 保存简单格式的丰富后完整大纲
            output_file = os.path.join(self.data_dir, "course_outline_enriched_simple.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump({
                    "msg": "请求成功",
                    "code": 200,
                    "data": outline_list
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n\n丰富课程大纲完成!")
            print(f"丰富后的简单格式大纲已保存到: {output_file}")
            
        else:
            # 原始嵌套格式处理方式
            total_courses = sum(len(stage.get('courseList', [])) for stage in outline_list)
            processed_courses = 0
            
            print(f"\n开始丰富课程大纲，共 {len(outline_list)} 个阶段, {total_courses} 个课程...")
            
            # 对每个阶段进行处理
            for stage in outline_list:
                course_list = stage.get('courseList', [])
                
                if course_list:
                    stage_title = stage.get('title', '未知阶段')
                    stage_id = stage.get('id', '未知')
                    
                    # 处理每个课程
                    for course in course_list:
                        course_id = course.get('id')
                        course_name = course.get('courseName', '未知课程')
                        
                        processed_courses += 1
                        progress = processed_courses / total_courses * 100
                        print(f"\r处理进度: {processed_courses}/{total_courses} ({progress:.1f}%) - 当前: {course_name}", end="")
                        
                        if course_id:
                            # 1. 获取课程版本信息
                            versions = self.fetch_course_versions(str(course_id))
                            
                            if versions and len(versions) > 0:
                                # 获取第一个版本的详细信息
                                version = versions[0]
                                version_id = version.get('id')
                                
                                # 添加详细描述到课程对象
                                course['pcDetailDesc'] = version.get('pcDetailDesc', '')
                                course['appDetailDesc'] = version.get('appDetailDesc', '')
                                course['versionId'] = version_id
                                course['versionName'] = version.get('name', '')
                                
                                # 记录章节ID与版本ID的映射关系
                                id_mapping[str(course_id)] = {
                                    'versionId': version_id,
                                    'courseName': course_name,
                                    'stageId': stage_id,
                                    'stageName': stage_title
                                }
                                
                                # 2. 获取课程详细章节信息
                                course_detail = self.fetch_course_detail(str(course_id), str(version_id))
                                if course_detail:
                                    # 添加详细章节信息到课程对象
                                    course['chapterList'] = course_detail.get('chapterList', [])
                                    course['durationSum'] = course_detail.get('durationSum', 0)
                                    course['level'] = course_detail.get('level', 0)
                                    course['price'] = course_detail.get('price', 0)
                                    course['studyCount'] = course_detail.get('studyCount', 0)
                                    
                                    # 计算总章节数和总小节数
                                    chapter_count = len(course['chapterList'])
                                    section_count = sum(len(chapter.get('sectionList', [])) for chapter in course['chapterList'])
                                    course['totalChapterCount'] = chapter_count
                                    course['totalSectionCount'] = section_count
            
            # 保存嵌套格式的丰富后完整大纲
            output_file = os.path.join(self.data_dir, "course_outline_enriched.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump({
                    "msg": "请求成功",
                    "code": 200,
                    "data": {
                        "stageList": outline_list
                    }
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n\n丰富课程大纲完成!")
            print(f"丰富后的完整大纲已保存到: {output_file}")
        
        # 保存ID映射关系到文件（这个文件是必要的，保留）
        mapping_file = os.path.join(self.data_dir, "course_version_mapping.json")
        with open(mapping_file, "w", encoding="utf-8") as f:
            json.dump(id_mapping, f, ensure_ascii=False, indent=2)
        print(f"课程ID与版本ID的映射关系已保存到: {mapping_file}")
        
        return outline_list

    def generate_markdown_from_enriched_json(self, json_file_path=None, output_file=None, max_chars_per_file=None):
        """从丰富的JSON数据生成Markdown格式的课程大纲
        
        Args:
            json_file_path: 输入的JSON文件路径，默认为course_outline_enriched_simple.json
            output_file: 输出的Markdown文件路径，默认为course_outline.md
            max_chars_per_file: 每个文件的最大字符数，如果为None则不分割文件
        
        Returns:
            list: 生成的Markdown文件路径列表
        """
        # 默认文件路径
        if json_file_path is None:
            json_file_path = os.path.join(self.data_dir, "course_outline_enriched_simple.json")
        
        if output_file is None:
            output_file = os.path.join(self.data_dir, "course_outline.md")
        
        # 读取JSON数据
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"错误: 文件 {json_file_path} 不存在")
            return None
        except json.JSONDecodeError:
            print(f"错误: 文件 {json_file_path} 不是有效的JSON格式")
            return None
        
        # 提取课程列表
        course_list = []
        if "data" in data and isinstance(data["data"], list):
            course_list = data["data"]
        elif "data" in data and "stageList" in data["data"]:
            # 尝试从stageList中提取课程
            stages = data["data"]["stageList"]
            for stage in stages:
                if "courseList" in stage:
                    course_list.extend(stage["courseList"])
        else:
            print("错误: JSON数据中没有找到课程列表")
            return None
        
        # 检查课程列表是否为空
        if not course_list:
            print("警告: 课程列表为空")
            return None
        
        # 生成目录内容
        toc_content = ["# 课程大纲总目录\n\n"]
        file_index = 1
        all_files = []
        
        # 通用文件名生成函数
        def get_filename(base_path, index):
            if index == 1:
                return base_path
            base_name, ext = os.path.splitext(base_path)
            return f"{base_name}_{index}{ext}"
        
        # 通用添加导航的函数
        def add_navigation(content, current_index, total_files):
            nav = ["## 文件导航\n\n"]
            if current_index > 1:
                prev_file = get_filename(output_file, current_index - 1)
                prev_name = os.path.basename(prev_file)
                nav.append(f"- [上一个文件 ({prev_name})]({prev_file})\n")
            
            if current_index < total_files:
                next_file = get_filename(output_file, current_index + 1)
                next_name = os.path.basename(next_file)
                nav.append(f"- [下一个文件 ({next_name})]({next_file})\n")
            
            nav.append(f"- [返回总目录]({os.path.basename(output_file)})\n\n")
            nav.append("---\n\n")
            
            return nav + content
        
        # 处理每个课程，准备切片
        all_course_contents = []
        for i, course in enumerate(course_list, 1):
            course_name = course.get("courseName", "未知课程")
            course_id = course.get("courseNo", "未知ID")
            
            # 清理course_name中的前导空格和换行符
            course_name = course_name.strip()
            
            # 为总目录添加课程项
            toc_content.append(f"{i}. **{course_name}** (ID: {course_id})\n")
            
            # 生成单个课程的内容
            course_content = []
            
            # 确保duration_total不为None
            duration_total = course.get("durationTotal")
            if duration_total is None:
                duration_total = 0
            
            # 格式化总时长
            hours = duration_total // 3600
            minutes = (duration_total % 3600) // 60
            seconds = duration_total % 60
            duration_str = f"{hours}小时{minutes}分钟{seconds}秒"
            
            # 添加课程标题和基本信息
            course_content.append(f"# {course_name}\n")
            course_content.append(f"- **课程ID**: {course_id}\n")
            course_content.append(f"- **总时长**: {duration_str}\n")
            
            # 如果有章节列表
            chapter_list = course.get("chapterList", [])
            if chapter_list:
                course_content.append("## 章节详情\n")
                for chapter_idx, chapter in enumerate(chapter_list, 1):
                    chapter_name = chapter.get("chapterName", "未知章节")
                    
                    # 清理chapter_name中的前导空格和换行符，确保标题效果正常
                    chapter_name = chapter_name.strip()
                    
                    chapter_count = chapter.get("chapterCount")
                    if chapter_count is None:
                        chapter_count = 0
                    
                    chapter_duration = chapter.get("chapterDurationTimeCount")
                    if chapter_duration is None:
                        chapter_duration = 0
                    
                    # 格式化章节时长
                    ch_hours = chapter_duration // 3600
                    ch_minutes = (chapter_duration % 3600) // 60
                    ch_seconds = chapter_duration % 60
                    ch_duration_str = f"{ch_hours}小时{ch_minutes}分钟{ch_seconds}秒"
                    
                    # 添加章节标题和基本信息
                    course_content.append(f"### {chapter_idx}. {chapter_name}\n")
                    course_content.append(f"- 时长: {ch_duration_str}\n")
                    course_content.append(f"- 小节数: {chapter_count}\n\n")
                    
                    # 处理每个小节
                    section_list = chapter.get("sectionList", [])
                    if section_list:
                        course_content.append("小节列表:\n")
                        for section_idx, section in enumerate(section_list, 1):
                            section_name = section.get("sectionName", "未知小节")
                            
                            # 清理section_name中的前导空格和换行符，确保加粗效果正常
                            section_name = section_name.strip()
                            
                            # 确保section_duration不为None
                            section_duration = section.get("durationTime")
                            if section_duration is None:
                                section_duration = 0
                            
                            # 格式化小节时长
                            sec_minutes = section_duration // 60
                            sec_seconds = section_duration % 60
                            sec_duration_str = f"{sec_minutes}分钟{sec_seconds}秒"
                            
                            course_content.append(f"  {section_idx}. **{section_name}** - {sec_duration_str}\n")
                    
                    course_content.append("\n")
            else:
                course_content.append("- **章节数**: 0\n")
                course_content.append("\n*该课程没有可用的章节信息*\n")
            
            course_content.append("\n---\n")
            
            # 将课程内容添加到列表
            all_course_contents.append("".join(course_content))
        
        # 生成时间
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp = f"\n*文档生成时间: {now}*\n"
        
        # 计算总字符数
        total_chars = sum(len(content) for content in all_course_contents) + len("".join(toc_content)) + len(timestamp)
        print(f"\n课程大纲总字符数: {total_chars} 个字符")
        
        # 如果未提供max_chars_per_file或为0，则不分割文件
        if max_chars_per_file is None or max_chars_per_file == 0:
            print("不进行文件分割，生成单个完整文件")
            # 把总目录内容完成
            toc_content.append("\n## 课程内容\n\n")
            toc_content.append(timestamp)
            
            # 写入完整文件（目录 + 所有课程内容）
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("".join(toc_content))
                f.write("\n---\n\n")
                f.write("".join(all_course_contents))
            
            print(f"\n课程大纲已成功生成为单个Markdown文件: {output_file}")
            return [output_file]
        
        # 进行文件分割
        print(f"进行文件分割，每个文件最大字符数: {max_chars_per_file}")
        # 把总目录内容完成
        toc_content.append("\n## 文件索引\n\n")
        
        # 进行切片处理
        current_content = []
        current_chars = 0
        total_files = 1  # 至少有一个文件
        
        # 先估算需要多少文件
        total_chars = sum(len(content) for content in all_course_contents) + len("".join(toc_content)) + len(timestamp)
        if total_chars > max_chars_per_file:
            total_files = (total_chars // max_chars_per_file) + 1
        
        # 更新总目录
        toc_file = output_file
        for file_idx in range(1, total_files + 1):
            file_path = get_filename(output_file, file_idx)
            file_name = os.path.basename(file_path)
            toc_content.append(f"- [课程大纲 第{file_idx}部分]({file_name})\n")
        
        toc_content.append(timestamp)
        
        # 写入总目录文件
        with open(toc_file, "w", encoding="utf-8") as f:
            f.write("".join(toc_content))
        all_files.append(toc_file)
        
        # 如果只有一个文件的情况（内容不多）
        if total_files == 1:
            content = "".join(all_course_contents)
            file_path = get_filename(output_file, 1)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content + timestamp)
            all_files = [file_path]
            print(f"\n课程大纲已成功生成为单个Markdown文件: {file_path}")
            return all_files
        
        # 处理需要多个文件的情况
        file_idx = 1
        current_file = get_filename(output_file, file_idx)
        current_content = []
        current_chars = 0
        
        for course_content in all_course_contents:
            # 如果当前课程内容加上已有内容超过限制，或者这是一个非常大的课程（单个课程超过限制）
            if current_chars + len(course_content) > max_chars_per_file and current_chars > 0:
                # 写入当前文件并开始新文件
                with open(current_file, "w", encoding="utf-8") as f:
                    content_with_nav = add_navigation(current_content, file_idx, total_files)
                    f.write("".join(content_with_nav) + timestamp)
                all_files.append(current_file)
                
                # 开始新文件
                file_idx += 1
                current_file = get_filename(output_file, file_idx)
                current_content = [course_content]
                current_chars = len(course_content)
            else:
                # 添加到当前文件
                current_content.append(course_content)
                current_chars += len(course_content)
        
        # 写入最后一个文件
        if current_content:
            with open(current_file, "w", encoding="utf-8") as f:
                content_with_nav = add_navigation(current_content, file_idx, total_files)
                f.write("".join(content_with_nav) + timestamp)
            all_files.append(current_file)
        
        print(f"\n课程大纲已成功生成为{len(all_files)}个Markdown文件:")
        for file_path in all_files:
            print(f"- {file_path}")
        
        return all_files

if __name__ == "__main__":
    try:
        mca = MCARequest()
        
        # 检查是否添加了命令行参数，支持直接生成MD文件的功能
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == "--generate-md":
            json_path = sys.argv[2] if len(sys.argv) > 2 else None
            md_path = sys.argv[3] if len(sys.argv) > 3 else None
            
            # 添加对分割参数的支持
            max_chars = 0  # 默认不分割
            if len(sys.argv) > 4:
                try:
                    max_chars = int(sys.argv[4])
                except ValueError:
                    print(f"警告: 无效的分割大小 '{sys.argv[4]}'，将使用默认值（不分割）")
            
            mca.generate_markdown_from_enriched_json(json_path, md_path, max_chars)
            sys.exit(0)
        
        # 步骤1: 获取课程列表并选择课程
        selected_course = mca.show_course_selection()
        if selected_course:
            mca.display_course_details(selected_course)
            course_id = selected_course.get('id')
            
            if course_id:
                # 步骤2: 获取选中课程的版本列表
                print(f"\n正在获取课程ID {course_id} 的版本列表...")
                selected_version = mca.show_course_package_versions(course_id)
                
                if selected_version:
                    mca.display_course_package_version(selected_version)
                    package_version_id = selected_version.get('id')
                    
                    if package_version_id:
                        # 步骤3: 获取课程大纲
                        print(f"\n正在获取课程大纲...")
                        
                        # 先尝试使用新API获取课程大纲
                        course_data = mca.fetch_course_child(course_id, package_version_id)
                        
                        if course_data:
                            print("\n使用新API成功获取课程大纲数据")
                            
                            # 检查可能的大纲结构
                            if 'stageList' in course_data:
                                outline_list = course_data.get('stageList', [])
                                if len(outline_list) == 0:
                                     outline_list = course_data.get('courseItemList', [])
                                print(f"找到课程阶段列表，共{len(outline_list)}个阶段")
                                mca.display_course_outline(outline_list)
                                mca.save_outline_for_download(outline_list, course_id, package_version_id)
                                
                                # 步骤4: 丰富课程大纲，获取每个课程的详细信息
                                print("\n\n是否需要获取每个课程的详细信息？(y/n): ")
                                enrich_option = input()
                                if enrich_option.lower() == 'y' or enrich_option.lower() == '':
                                    print("\n正在获取每个课程的详细信息...")
                                    enriched_outline = mca.enrich_course_outline(outline_list)
                                    
                                    # 步骤5: 生成Markdown大纲
                                    print("\n\n是否需要生成Markdown格式的课程大纲？(y/n): ")
                                    md_option = input()
                                    if md_option.lower() == 'y' or md_option.lower() == '':
                                        print("\n正在生成Markdown大纲...")
                                        
                                        # 询问是否需要分割文件
                                        print("\n请选择文件分割方式：")
                                        print("1. 不分割，生成单个完整文件")
                                        print("2. 按指定字数分割")
                                        split_option = input("请选择（默认为1）: ")
                                        
                                        max_chars = 0  # 默认不分割
                                        if split_option == "2":
                                            char_input = input("请输入每个文件的最大字符数（默认20000）: ")
                                            try:
                                                max_chars = int(char_input) if char_input.strip() else 20000
                                            except ValueError:
                                                print(f"无效的输入 '{char_input}'，使用默认值20000")
                                                max_chars = 20000
                                        
                                        if 'courseNo' in outline_list[0]:
                                            # 简单列表格式
                                            mca.generate_markdown_from_enriched_json(max_chars_per_file=max_chars)
                                        else:
                                            # 嵌套格式
                                            mca.generate_markdown_from_enriched_json(
                                                os.path.join(mca.data_dir, "course_outline_enriched.json"),
                                                max_chars_per_file=max_chars
                                            )
                            elif 'courseItemList' in course_data:
                                outline_list = course_data.get('courseItemList', [])
                                print(f"找到课程列表，共{len(outline_list)}个课程")
                                mca.display_course_outline(outline_list)
                                mca.save_outline_for_download(outline_list, course_id, package_version_id)
                                
                                # 对于courseItemList也添加生成Markdown的选项
                                print("\n\n是否需要获取每个课程的详细信息？(y/n): ")
                                enrich_option = input()
                                if enrich_option.lower() == 'y' or enrich_option.lower() == '':
                                    print("\n正在获取每个课程的详细信息...")
                                    enriched_outline = mca.enrich_course_outline(outline_list)
                                    
                                    print("\n\n是否需要生成Markdown格式的课程大纲？(y/n): ")
                                    md_option = input()
                                    if md_option.lower() == 'y' or md_option.lower() == '':
                                        print("\n正在生成Markdown大纲...")
                                        
                                        # 询问是否需要分割文件
                                        print("\n请选择文件分割方式：")
                                        print("1. 不分割，生成单个完整文件")
                                        print("2. 按指定字数分割")
                                        split_option = input("请选择（默认为1）: ")
                                        
                                        max_chars = 0  # 默认不分割
                                        if split_option == "2":
                                            char_input = input("请输入每个文件的最大字符数（默认20000）: ")
                                            try:
                                                max_chars = int(char_input) if char_input.strip() else 20000
                                            except ValueError:
                                                print(f"无效的输入 '{char_input}'，使用默认值20000")
                                                max_chars = 20000
                                        
                                        mca.generate_markdown_from_enriched_json(max_chars_per_file=max_chars)
                            else:
                                print("无法识别的课程大纲结构，请查看保存的JSON文件进行分析")
                        else:
                            # 如果新API失败，尝试使用旧API
                            print("\n新API获取失败，尝试使用旧API...")
                            outline_list = mca.get_course_outline(package_version_id)
                            
                            if outline_list:
                                print("\n" + "="*80)
                                print("课程大纲".center(78))
                                print("="*80)
                                mca.display_course_outline(outline_list)
                                print("="*80)
                                
                                # 保存大纲到扁平结构，便于后续处理
                                mca.save_outline_for_download(outline_list, course_id, package_version_id)
                                
                                # 对于旧API结果也添加生成Markdown的选项
                                print("\n\n是否需要获取每个课程的详细信息？(y/n): ")
                                enrich_option = input()
                                if enrich_option.lower() == 'y' or enrich_option.lower() == '':
                                    print("\n正在获取每个课程的详细信息...")
                                    enriched_outline = mca.enrich_course_outline(outline_list)
                                    
                                    print("\n\n是否需要生成Markdown格式的课程大纲？(y/n): ")
                                    md_option = input()
                                    if md_option.lower() == 'y' or md_option.lower() == '':
                                        print("\n正在生成Markdown大纲...")
                                        
                                        # 询问是否需要分割文件
                                        print("\n请选择文件分割方式：")
                                        print("1. 不分割，生成单个完整文件")
                                        print("2. 按指定字数分割")
                                        split_option = input("请选择（默认为1）: ")
                                        
                                        max_chars = 0  # 默认不分割
                                        if split_option == "2":
                                            char_input = input("请输入每个文件的最大字符数（默认20000）: ")
                                            try:
                                                max_chars = int(char_input) if char_input.strip() else 20000
                                            except ValueError:
                                                print(f"无效的输入 '{char_input}'，使用默认值20000")
                                                max_chars = 20000
                                        
                                        mca.generate_markdown_from_enriched_json(max_chars_per_file=max_chars)
                            else:
                                print("\n未找到标准大纲列表，但已保存可用的课程信息。")
                                print("您可以在data目录中查看保存的课程信息，或者继续尝试下一步操作。")
                                
                                # 获取下一个API需要的基本信息
                                print("\n" + "="*80)
                                print("课程基本信息".center(78))
                                print("="*80)
                                print(f"课程ID: {course_id}")
                                print(f"课程包版本ID: {package_version_id}")
                                print("="*80)
                                
                                # 询问是否继续下一步
                                continue_option = input("\n是否继续执行下一步操作？(y/n): ")
                                if continue_option.lower() != 'y':
                                    print("操作已取消")
    except Exception as e:
        print(f"发生错误: {e}")
        
        # 添加详细错误信息
        import traceback
        print("\n详细错误信息:")
        traceback.print_exc() 