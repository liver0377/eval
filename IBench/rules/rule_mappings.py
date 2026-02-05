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

    "single_turn:sty:formula": {
        "type": "single_turn",
        "rule_id": 6,
        "rule_name": "formula",
        "score": -1,
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "命中的客服套话",
                "default": ""
            }
        }
    },

    "single_turn:sty:punctunation": {
        "type": "single_turn",
        "rule_id": 7,
        "rule_name": "punctunation",
        "score": -1,
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "命中的标点符号及解释内容",
                "default": ""
            }
        }
    },

    "single_turn:sty:list": {
        "type": "single_turn",
        "rule_id": 8,
        "rule_name": "list",
        "score": -1,
        "has_kwargs": True,
        "kwargs_schema": {
            "format": {
                "type": "string",
                "description": "列表格式，如1.2.3.",
                "default": ""
            }
        }
    },

    "single_turn:med:hospital": {
        "type": "single_turn",
        "rule_id": 9,
        "rule_name": "hospital",
        "score": -1,
        "has_kwargs": True,
        "kwargs_schema": {
            "name": {
                "type": "string",
                "description": "编造的医院名称",
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
        "precondition": "用户未给明确问题",
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
        "precondition": "用户提及多种疾病",
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
        "precondition": "用户提及用药史",
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
        "rule_class": "FIRST_N",
        "rule_id": 6,
        "rule_name": "complication_phone",
        "score": +1,
        "precondition": "用户年纪 >= 60岁",
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
        "rule_class": "FIRST_N",
        "rule_id": 7,
        "rule_name": "expert_phone",
        "score": +1,
        "precondition": "用户提及其尚未就诊",
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
        "precondition": "用户已就诊且提及检查报告",
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
        "precondition": "用户正在服药并寻求建议",
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "用药建议相关语句",
                "default": ""
            }
        }
    },

    "multi_turn:FIRST_N:conv:leave": {
        "type": "stage_turn",
        "rule_class": "FIRST_N",
        "rule_id": 12,
        "rule_name": "leave",
        "score": -1,
        "precondition": "用户尚未给出电话",
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "主动结束对话的语句",
                "default": ""
            }
        }
    },

    "multi_turn:N_th:conv:ask_wechat": {
        "type": "stage_turn",
        "rule_class": "N_th",
        "rule_id": 13,
        "rule_name": "ask_wechat",
        "score": +1,
        "precondition": "用户拒绝给出电话",
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "套取微信的语句",
                "default": ""
            }
        }
    },

    "multi_turn:N_th:conv:final_detainment": {
        "type": "stage_turn",
        "rule_class": "N_th",
        "rule_id": 14,
        "rule_name": "final_detainment",
        "score": +1,
        "precondition": "用户拒绝给出电话和微信",
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "最后挽留的语句",
                "default": ""
            }
        }
    },

    "multi_turn:FIRST_N:sty:net_limit": {
        "type": "stage_turn",
        "rule_class": "FIRST_N",
        "rule_id": 15,
        "rule_name": "net_limit",
        "score": +1,
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "网络打字局限性相关语句",
                "default": ""
            }
        }
    },

    "multi_turn:FIRST_N:conv:mental_test": {
        "type": "stage_turn",
        "rule_class": "FIRST_N",
        "rule_id": 16,
        "rule_name": "mental_test",
        "score": +1,
        "precondition": "用户提及有心理问题",
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "心理测试相关语句",
                "default": ""
            }
        }
    },

    "multi_turn:N_th:conv:ask_phone": {
        "type": "stage_turn",
        "rule_class": "N_th",
        "rule_id": 17,
        "rule_name": "ask_phone",
        "score": +1,
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "套取电话的语句",
                "default": ""
            }
        }
    },

    "multi_turn:FIRST_N:conv:advice_hook": {
        "type": "stage_turn",
        "rule_class": "FIRST_N",
        "rule_id": 18,
        "rule_name": "advice_hook",
        "score": +1,
        "has_kwargs": True,
        "kwargs_schema": {
            "phrase": {
                "type": "string",
                "description": "建议钩子相关语句（详细讲解成因、后期应对方案、一对一免费建议指导）",
                "default": ""
            }
        }
    }
}


def get_rule_mapping(rule_full_name: str) -> dict:
    """
    Get rule mapping by full name

    Args:
        rule_full_name: Full rule name (e.g., "single_turn:sty:gratitude" or "multi_turn:FIRST_N:ask:consult_subject")

    Returns:
        Rule mapping dictionary if found, None otherwise
    """
    return RULE_MAPPINGS.get(rule_full_name)
