"""
Rule Mapping Configuration
Maps rule names to rule definitions with semantic clustering
"""

# 规则映射配置
# 新格式: "single_turn:category:rule_name" 或 "multi_turn:{FIRST_N|N_th}:{category}:{rule_name}"
RULE_MAPPINGS = {
    # ========== 单轮规则映射 ==========
    
    "single_turn:sty:gratitude": {
        "type": "single_turn",
        "rule_id": 1,
        "rule_name": "gratitude",
        "score": -1,
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "命中的感谢词",
                "default": ""
            }
        }
    },
    
    "single_turn:sty:explain_filler": {
        "type": "single_turn",
        "rule_id": 2,
        "rule_name": "explain_filler",
        "score": -1,
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "命中的解释性套话",
                "default": ""
            }
        }
    },
    
    "single_turn:med:forced_symptom": {
        "type": "single_turn",
        "rule_id": 3,
        "rule_name": "forced_symptom",
        "score": -1,
        "has_kwargs": True,
        "kwargs_schema": {
            "query_type": {
                "type": "enum",
                "values": ["list", "yesno"],
                "description": "问症状列表/问有无",
                "default": "unknown"
            }
        }
    },
    
    "single_turn:ask:multi_question": {
        "type": "single_turn",
        "rule_id": 4,
        "rule_name": "multi_question",
        "score": -1,
        "has_kwargs": True,
        "kwargs_schema": {
            "q_cnt": {
                "type": "int",
                "description": "问题数量",
                "default": 0
            }
        }
    },
    
    "single_turn:med:diagnosis_name": {
        "type": "single_turn",
        "rule_id": 5,
        "rule_name": "diagnosis_name",
        "score": -1,
        "has_kwargs": True,
        "kwargs_schema": {
            "dx": {
                "type": "string",
                "description": "提到的疾病名称",
                "default": ""
            }
        }
    },

    # ========== 阶段规则映射（语义聚类版） ==========
    
    # ask 聚类
    "multi_turn:FIRST_N:ask:consult_subject": {
        "type": "stage_turn",
        "rule_class": "FIRST_N",
        "rule_id": 1,
        "rule_name": "consult_subject",
        "score": +1,
        "has_kwargs": True,
        "kwargs_schema": {
            "who": {
                "type": "enum",
                "values": ["self", "family", "other", "unknown"],
                "description": "咨询对象",
                "default": "unknown"
            }
        }
    },
    
    "multi_turn:N_th:ask:prompt_question": {
        "type": "stage_turn",
        "rule_class": "N_th",
        "rule_id": 9,
        "rule_name": "prompt_question",
        "score": +1,
        "has_kwargs": True,
        "kwargs_schema": {
            "prompt": {
                "type": "enum",
                "values": ["discomfort", "main_question", "open"],
                "description": "引导类型",
                "default": "open"
            }
        }
    },
    
    # med 聚类
    "multi_turn:FIRST_N:med:visit_history": {
        "type": "stage_turn",
        "rule_class": "FIRST_N",
        "rule_id": 2,
        "rule_name": "visit_history",
        "score": -1,
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "提及的就诊史相关语句",
                "default": ""
            }
        }
    },
    
    "multi_turn:N_th:med:test_invite": {
        "type": "stage_turn",
        "rule_class": "N_th",
        "rule_id": 3,
        "rule_name": "test_invite",
        "score": -1,
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "检查邀约的类型",
                "default": ""
            }
        }
    },
    
    # demo 聚类
    "multi_turn:N_th:demo:gender": {
        "type": "stage_turn",
        "rule_class": "N_th",
        "rule_id": 4,
        "rule_name": "gender",
        "score": +1,
        "has_kwargs": True,
        "kwargs_schema": {
            "gender": {
                "type": "enum",
                "values": ["male", "female", "unknown"],
                "description": "询问到的性别",
                "default": "unknown"
            }
        }
    },
    
    # scope 聚类
    "multi_turn:FIRST_N:scope:primary_only": {
        "type": "stage_turn",
        "rule_class": "FIRST_N",
        "rule_id": 8,
        "rule_name": "primary_only",
        "score": +1,
        "has_kwargs": True,
        "kwargs_schema": {
            "main_disease": {
                "type": "string",
                "description": "机器人聚焦的主症/主题",
                "default": ""
            }
        }
    },
    
    # conv 聚类
    "multi_turn:FIRST_N:conv:medication_phone": {
        "type": "stage_turn",
        "rule_class": "FIRST_N",
        "rule_id": 5,
        "rule_name": "medication_phone",
        "score": +1,
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "用药相关语句",
                "default": ""
            }
        }
    },
    
    "multi_turn:FIRST_N:conv:complication_phone": {
        "type": "stage_turn",
        "rule_class": "FIRST_N,
        "rule_id": 6,
        "rule_name": "complication_phone",
        "score": +1,
        "has_kwargs": True,
        "kwargs_schema": {
            "disease": {
                "type": "string",
                "description": "提到的并发症疾病",
                "default": ""
            }
        }
    },
    
    "multi_turn:FIRST_N:conv:expert_phone": {
        "type": "stage_turn",
        "rule_class": "FIRST_N,
        "rule_id": 7,
        "rule_name": "expert_phone",
        "score": +1,
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "专家解读相关语句",
                "default": ""
            }
        }
    },
    
    "multi_turn:N_th:conv:report_phone": {
        "type": "stage_turn",
        "rule_class": "N_th",
        "rule_id": 10,
        "rule_name": "report_phone",
        "score": +1,
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "报告建议和套电话语句",
                "default": ""
            }
        }
    },
    
    "multi_turn:N_th:conv:advice_phone": {
        "type": "stage_turn",
        "rule_class": "N_th",
        "rule_id": 11,
        "rule_name": "advice_phone",
        "score": +1,
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "用药建议相关语句",
                "default": ""
            }
        }
    }
}