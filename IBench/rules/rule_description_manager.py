"""
规则描述管理器
统一管理规则描述的加载、替换和缓存
"""
import json
from pathlib import Path
from typing import Optional
from functools import lru_cache


class RuleDescriptionManager:
    """规则描述管理器
    
    从 system_prompt.json 加载描述模板，
    并支持动态 {N} 值替换
    """
    
    def __init__(self, template_path: str = "data/dataset/system_prompt.json"):
        """
        初始化描述管理器
        
        Args:
            template_path: 描述模板文件路径
        """
        self.template_path = Path(template_path)
        self._templates = None
        self._rule_to_category = {}  # 规则名到分类的映射
    
    @property
    def templates(self) -> dict:
        """懒加载模板"""
        if self._templates is None:
            if self.template_path.exists():
                with open(self.template_path, 'r', encoding='utf-8') as f:
                    self._templates = json.load(f)
                
                # 构建规则名到分类的映射
                self._build_rule_mapping()
            else:
                self._templates = {}
        return self._templates
    
    def _build_rule_mapping(self):
        """构建规则名到分类的映射"""
        for category, rules in self.templates.items():
            for rule_key, description in rules.items():
                self._rule_to_category[rule_key] = category
    
    def get_description(
        self,
        rule_full_name: str,
        base_description: str,
        N: Optional[int] = None
    ) -> str:
        """
        获取动态规则描述
        
        Args:
            rule_full_name: 完整规则名称
                - 单轮: "single_turn:sty:gratitude"
                - 阶段: "multi_turn:FIRST_N:ask:consult_subject"
            base_description: 基础描述（fallback）
            N: 可选的N值
        
        Returns:
            动态规则描述（已替换{N}）
        """
        # 1. 确定分类
        category = self._get_category(rule_full_name)
        if category is None:
            return base_description
        
        # 2. 查找模板
        if category not in self.templates:
            return base_description
        
        template = self.templates[category].get(rule_full_name)
        if not template:
            return base_description
        
        # 3. 替换{N}
        if N is not None and "{N}" in template:
            return template.replace("{N}", str(N))
        
        return template
    
    def _get_category(self, rule_full_name: str) -> Optional[str]:
        """
        根据完整规则名确定分类
        
        Args:
            rule_full_name: 完整规则名称
        
        Returns:
            分类名称 ("[语言风格与去AI味规范]" 或 "[留联约束]")
        """
        if rule_full_name in self._rule_to_category:
            return self._rule_to_category[rule_full_name]
        
        # 根据前缀判断
        if rule_full_name.startswith("single_turn"):
            return "[语言风格与去AI味规范]"
        elif rule_full_name.startswith("multi_turn"):
            return "[留联约束]"
        
        return None
    
    @lru_cache(maxsize=100)
    def get_description_cached(
        self,
        rule_full_name: str,
        base_description: str,
        N: Optional[int] = None
    ) -> str:
        """带缓存的版本"""
        return self.get_description(rule_full_name, base_description, N)


# 全局单例
_description_manager = None


def get_description_manager() -> RuleDescriptionManager:
    """获取全局描述管理器单例"""
    global _description_manager
    if _description_manager is None:
        _description_manager = RuleDescriptionManager()
    return _description_manager
