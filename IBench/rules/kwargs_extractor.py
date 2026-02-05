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
            # 单轮规则
            "single_turn:sty:gratitude": self._extract_phrase,
            "single_turn:sty:explain_filler": self._extract_phrase,
            "single_turn:med:forced_symptom": self._extract_query_type,
            "single_turn:ask:multi_question": self._extract_q_cnt,
            "single_turn:med:diagnosis_name": self._extract_dx,
            
            # 阶段规则 - FIRST_N
            "multi_turn:FIRST_N:consult_subject": self._extract_who,
            "multi_turn:FIRST_N:visit_history": self._extract_phrase,
            "multi_turn:FIRST_N:test_invite": self._extract_phrase,
            "multi_turn:FIRST_N:gender": self._extract_gender,
            "multi_turn:FIRST_N:medication_phone": self._extract_phrase,
            "multi_turn:FIRST_N:complication_phone": self._extract_disease,
            "multi_turn:FIRST_N:expert_phone": self._extract_phrase,
            "multi_turn:FIRST_N:primary_only": self._extract_main_disease,
            "multi_turn:FIRST_N:prompt_question": self._extract_prompt,
            "multi_turn:FIRST_N:report_phone": self._extract_phrase,
            "multi_turn:FIRST_N:advice_phone": self._extract_phrase,
            
            # 阶段规则 - N_th
            "multi_turn:N_th:consult_subject": self._extract_who,
            "multi_turn:N_th:visit_history": self._extract_phrase,
            "multi_turn:N_th:test_invite": self._extract_phrase,
            "multi_turn:N_th:gender": self._extract_gender,
            "multi_turn:N_th:medication_phone": self._extract_phrase,
            "multi_turn:N_th:complication_phone": self._extract_disease,
            "multi_turn:N_th:expert_phone": self._extract_phrase,
            "multi_turn:N_th:primary_only": self._extract_main_disease,
            "multi_turn:N_th:prompt_question": self._extract_prompt,
            "multi_turn:N_th:report_phone": self._extract_phrase,
            "multi_turn:N_th:advice_phone": self._extract_phrase,
            
            # 兼容旧格式
            "multi_turn:policy_universe:ask_gender": self._extract_gender,
            "multi_turn:policy_universe:inquire_target": self._extract_who,
            "multi_turn:policy_universe:emotional_comfort": self._extract_emotion_type,
            "multi_turn:policy_universe:ask_symptom": self._extract_symptoms,
            "multi_turn:policy_universe:disease_diagnosis": self._extract_disease,
            "multi_turn:policy_universe:examination_invitation": self._extract_examination_type,
            "multi_turn:policy_universe:collect_phone_medication": self._extract_medication_info,
            "multi_turn:policy_universe:collect_phone_complication": self._extract_complication_type,
            "multi_turn:policy_universe:collect_phone_expert_interpretation": self._extract_expert_type,
            "multi_turn:policy_universe:mention_visit_history": self._extract_visit_mentioned,
            "multi_turn:policy_universe:explanatory_statements": self._extract_explanation_detected,
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
    
    def _extract_target(self, response: str, conversation: List[Message]) -> dict:
        """
        Extract consultation target (self/family)

        Returns: {'target': 'self'/'family'/'unknown'}
        """
        return self._extract_who(response, conversation)
    
    def _extract_emotion_type(self, response: str, conversation: List[Message]) -> dict:
        """
        Extract emotion comfort type

        Returns: {'emotion_type': string}
        """
        emotion_keywords = {
            '安慰': '安慰',
            '担心': '宽慰',
            '别担心': '宽慰',
            '不用怕': '鼓励',
            '理解': '共情',
        }

        for keyword, emotion_type in emotion_keywords.items():
            if keyword in response:
                return {'emotion_type': emotion_type}

        return {'emotion_type': ''}
    
    def _extract_symptoms(self, response: str, conversation: List[Message]) -> dict:
        """
        Extract symptoms asked in response

        Returns: {'symptoms_asked': list}
        """
        symptoms = []

        symptom_keywords = [
            '失眠', '头痛', '发烧', '咳嗽', '疼痛', '乏力',
            '恶心', '呕吐', '腹泻', '便秘', '头晕'
        ]

        for symptom in symptom_keywords:
            if symptom in response:
                symptoms.append(symptom)

        return {'symptoms_asked': symptoms}
    
    def _extract_disease(self, response: str, conversation: List[Message]) -> dict:
        """
        Extract mentioned disease name

        Returns: {'disease_mentioned': string}
        """
        return self._extract_dx(response, conversation)
    
    def _extract_examination_type(self, response: str, conversation: List[Message]) -> dict:
        """
        Extract examination invitation type

        Returns: {'examination_type': string}
        """
        exam_keywords = {
            '体检': '体检',
            '检查': '检查',
            '化验': '化验',
            '测试': '测试',
            '诊断': '诊断'
        }

        for keyword, exam_type in exam_keywords.items():
            if keyword in response:
                return {'examination_type': exam_type}

        return {'examination_type': ''}
    
    def _extract_medication_info(self, response: str, conversation: List[Message]) -> dict:
        """
        Extract medication-related information

        Returns: {'medication_mentioned': bool, 'phone_collected': bool}
        """
        medication_keywords = ['药', '吃药', '服药', '药物', '用药']
        phone_keywords = ['电话', '联系方式', '微信', '手机']

        medication_mentioned = any(kw in response for kw in medication_keywords)
        phone_collected = any(kw in response for kw in phone_keywords)

        return {
            'medication_mentioned': medication_mentioned,
            'phone_collected': phone_collected
        }
    
    def _extract_complication_type(self, response: str, conversation: List[Message]) -> dict:
        """
        Extract complication type mentioned

        Returns: {'complication_type': string}
        """
        complication_keywords = {
            '并发症': '并发症',
            '后遗症': '后遗症',
            '副作用': '副作用',
            '不良反应': '不良反应'
        }

        for keyword, comp_type in complication_keywords.items():
            if keyword in response:
                return {'complication_type': comp_type}

        return {'complication_type': ''}
    
    def _extract_expert_type(self, response: str, conversation: List[Message]) -> dict:
        """
        Extract expert interpretation type

        Returns: {'expert_type': string}
        """
        if '专家' in response:
            return {'expert_type': '专家'}
        elif '医生' in response:
            return {'expert_type': '医生'}
        elif '真人' in response:
            return {'expert_type': '真人'}

        return {'expert_type': ''}
    
    def _extract_visit_mentioned(self, response: str, conversation: List[Message]) -> dict:
        """
        Extract whether visit history was mentioned

        Returns: {'visit_mentioned': bool}
        """
        visit_keywords = ['去过医院', '看过医生', '就诊', '医院', '检查过']
        visit_mentioned = any(kw in response for kw in visit_keywords)

        return {'visit_mentioned': visit_mentioned}
    
    def _extract_explanation_detected(self, response: str, conversation: List[Message]) -> dict:
        """
        Extract whether explanatory statements were detected

        Returns: {'explanation_detected': bool}
        """
        explanation_keywords = ['这有助于', '了解到', '说明', '因为', '由于']
        explanation_detected = any(kw in response for kw in explanation_keywords)

        return {'explanation_detected': explanation_detected}
