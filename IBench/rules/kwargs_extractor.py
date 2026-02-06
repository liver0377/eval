"""
Kwargs Extractor
Extracts keyword arguments from responses and conversations
"""

import re
from typing import List, Dict, Any, Optional
from IBench.utils.common import Message


class KwargsExtractor:
    """Extract kwargs from responses based on rule schema"""

    def __init__(self, llm_judge=None):
        """
        Initialize kwargs extractor

        Args:
            llm_judge: Optional LLM judge for complex extractions
        """
        self.llm_judge = llm_judge

    def extract(
        self,
        rule_full_name: str,
        kwargs_schema: dict,
        response: str,
        conversation: List[Message]
    ) -> dict:
        """
        Extract kwargs for a specific rule

        Args:
            rule_full_name: Full rule name
                单轮规则: "single_turn:sty:gratitude"
                阶段规则: "multi_turn:FIRST_N:consult_subject" 或 "multi_turn:N_th:gender"
            kwargs_schema: Schema defining expected kwargs
            response: Assistant's response
            conversation: Full conversation history

        Returns:
            Extracted kwargs dict
        """
        # 根据规则名称选择提取方法
        extractor_map = {
            # ========== 单轮规则 (9条) ==========
            "single_turn:sty:gratitude": self._extract_phrase,
            "single_turn:sty:explain_filler": self._extract_phrase,
            "single_turn:sty:formula": self._extract_phrase,
            "single_turn:sty:punctuation": self._extract_phrase,
            "single_turn:sty:list": self._extract_format,
            "single_turn:med:forced_symptom": self._extract_query_type,
            "single_turn:med:diagnosis_name": self._extract_dx,
            "single_turn:med:hospital": self._extract_hospital_name,
            "single_turn:ask:multi_question": self._extract_q_cnt,
            
            # ========== 阶段规则 - FIRST_N (12条) ==========
            "multi_turn:FIRST_N:ask:consult_subject": self._extract_who,
            "multi_turn:FIRST_N:ask:prompt_question": self._extract_prompt,
            "multi_turn:FIRST_N:med:visit_history": self._extract_phrase_with_pre,
            "multi_turn:FIRST_N:med:test_invite": self._extract_phrase_with_pre,
            "multi_turn:FIRST_N:demo:gender": self._extract_gender,
            "multi_turn:FIRST_N:scope:primary_only": self._extract_main_disease,
            "multi_turn:FIRST_N:conv:complication_phone": self._extract_disease_with_age,
            "multi_turn:FIRST_N:conv:expert_phone": self._extract_phrase_with_pre,
            "multi_turn:FIRST_N:conv:advice_hook": self._extract_phrase,
            "multi_turn:FIRST_N:conv:leave": self._extract_phrase,
            "multi_turn:FIRST_N:sty:net_limit": self._extract_phrase,
            
            # ========== 阶段规则 - N_th (8条) ==========
            "multi_turn:N_th:conv:medication_phone": self._extract_phrase_with_pre,
            "multi_turn:N_th:conv:report_phone": self._extract_phrase_with_pre,
            "multi_turn:N_th:conv:ask_phone": self._extract_phrase,
            "multi_turn:N_th:conv:ask_wechat": self._extract_phrase_with_pre,
            "multi_turn:N_th:conv:final_detainment": self._extract_phrase_with_pre,
            "multi_turn:N_th:conv:hospital_information": self._extract_phrase,
            "multi_turn:N_th:conv:mental_test": self._extract_phrase_with_pre,
        }

        extractor = extractor_map.get(rule_full_name)
        if extractor:
            return extractor(response, conversation)
        else:
            # 默认返回空dict，使用schema中的默认值
            return self._get_default_kwargs(kwargs_schema)

    def _get_default_kwargs(self, kwargs_schema: dict) -> dict:
        """
        Get default values from schema

        Args:
            kwargs_schema: Schema defining kwargs

        Returns:
            Dict with default values
        """
        defaults = {}
        for key, config in kwargs_schema.items():
            defaults[key] = config.get('default', '' if config.get('type') == 'string' else None)
        return defaults

    # ========== 新增提取方法 ==========
    
    def _extract_phrase(self, response: str, conversation: List[Message]) -> dict:
        """提取关键短语"""
        return {'phrase': response[:100]}  # 简化处理，实际可以用LLM提取关键句
    
    def _extract_query_type(self, response: str, conversation: List[Message]) -> dict:
        """提取问询类型"""
        if '有什么' in response or '哪些' in response:
            return {'query_type': 'list'}
        elif '有没有' in response or '是否' in response or '是不是' in response:
            return {'query_type': 'yesno'}
        return {'query_type': 'unknown'}
    
    def _extract_q_cnt(self, response: str, conversation: List[Message]) -> dict:
        """提取问题数量"""
        q_cnt = response.count('？') + response.count('?')
        return {'q_cnt': q_cnt}
    
    def _extract_dx(self, response: str, conversation: List[Message]) -> dict:
        """提取疾病名称"""
        disease_keywords = ['感冒', '流感', '高血压', '糖尿病', '胃炎', '肺炎', '支气管炎', '失眠症', '抑郁症']
        for disease in disease_keywords:
            if disease in response:
                return {'dx': disease}
        return {'dx': ''}
    
    def _extract_who(self, response: str, conversation: List[Message]) -> dict:
        """提取咨询对象"""
        if '本人' in response or '自己' in response:
            return {'who': 'self'}
        elif '孩子' in response or '家人' in response or '亲属' in response:
            return {'who': 'family'}
        elif '朋友' in response or '同事' in response:
            return {'who': 'other'}
        return {'who': 'unknown'}
    
    def _extract_main_disease(self, response: str, conversation: List[Message]) -> dict:
        """提取主要病症"""
        return {'main_disease': response[:50]}
    
    def _extract_prompt(self, response: str, conversation: List[Message]) -> dict:
        """提取引导类型"""
        if '不适' in response:
            return {'prompt': 'discomfort'}
        elif '问题' in response:
            return {'prompt': 'main_question'}
        return {'prompt': 'open'}
    
    def _extract_format(self, response: str, conversation: List[Message]) -> dict:
        """提取列表格式"""
        list_patterns = ['1.', '2.', '3.', '一、', '二、', '三、', '①', '②', '③']
        format_found = ''
        for pattern in list_patterns:
            if pattern in response:
                format_found = pattern
                break
        return {'format': format_found}
    
    def _extract_hospital_name(self, response: str, conversation: List[Message]) -> dict:
        """提取编造的医院名称"""
        hospital_keywords = ['医院', '诊所', '中心', '门诊']
        for keyword in hospital_keywords:
            if keyword in response:
                return {'name': f'包含"{keyword}"的医院名称'}
        return {'name': ''}
    
    def _extract_phrase_with_pre(self, response: str, conversation: List[Message]) -> dict:
        """提取关键短语（包含前置短语）"""
        return {
            'phrase': response[:100],
            'pre_phrase': ''
        }
    
    def _extract_disease_with_age(self, response: str, conversation: List[Message]) -> dict:
        """提取疾病名称（包含年龄阈值）"""
        disease_keywords = ['高血压', '糖尿病', '心脏病', '脑梗', '中风']
        for disease in disease_keywords:
            if disease in response:
                return {'disease': disease, 'age': 60}
        return {'disease': '', 'age': 60}
    
    # ========== 保留旧方法以兼容 ==========
    
    def _extract_gender(self, response: str, conversation: List[Message]) -> dict:
        """
        Extract gender from response

        Returns: {'gender': 'male'/'female'/'unknown'}
        """
        if '男' in response or '先生' in response:
            return {'gender': 'male'}
        elif '女' in response or '女士' in response or '小姐' in response:
            return {'gender': 'female'}
        return {'gender': 'unknown'}
    
