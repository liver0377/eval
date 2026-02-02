"""
Test script to verify remove_thinking_content works for different models.
"""
import sys
sys.path.insert(0, 'C:/Users/wudw/Documents/company/eval/FastChat_Ours')

from fastchat.llm_judge.gen_model_answer import remove_thinking_content


def test_qwen_with_thinking():
    """Test Qwen model with thinking process"""
    text = """好的，用户现在说他最近压力很大，情绪快崩溃了。首先，我需要表现出同理心。
他提到压力大和情绪崩溃，这可能涉及心理问题，比如焦虑或抑郁。
我需要先确认他的情绪状态，是否有自伤或伤害他人的想法。


我能感受到你最近承受了很大的压力，这种状态确实会让人感到非常疲惫和无助。首先想告诉你，你的感受是真实且重要的，很多人都会在生活的某个阶段经历类似的困扰。

如果你愿意的话，可以和我聊聊具体是什么让你感到压力？"""
    
    result = remove_thinking_content(text, "Qwen3-8B")
    assert "我能感受到" in result, "Should keep answer"
    assert "好的，用户" not in result, "Should remove thinking"
    print("✅ Qwen with thinking: PASS")
    return True


def test_qwen_without_separator():
    """Test Qwen model without separator (should keep original)"""
    text = """我能感受到你最近承受了很大的压力，这种状态确实会让人感到非常疲惫和无助。首先想告诉你，你的感受是真实且重要的，很多人都会在生活的某个阶段经历类似的困扰。"""
    
    result = remove_thinking_content(text, "Qwen3-8B")
    assert result == text, "Should keep original if no separator"
    print("✅ Qwen without separator: PASS")
    return True


def test_sft_with_thinking():
    """Test SFT model with thinking process"""
    text = """让我分析一下这个问题。用户询问的是如何解决编程问题。
首先，我需要理解用户的需求，然后提供解决方案。
最后，我会给出具体的代码示例。


根据你的描述，这里有一个简单的解决方案：
1. 首先检查输入参数
2. 然后使用循环处理
3. 最后返回结果"""
    
    result = remove_thinking_content(text, "MySFTModel")
    assert "根据你的描述" in result, "Should keep answer"
    assert "让我分析" not in result, "Should remove thinking"
    print("✅ SFT with thinking: PASS")
    return True


def test_sft_without_thinking():
    """Test SFT model without thinking process"""
    text = """根据你的描述，这里有一个简单的解决方案：
1. 首先检查输入参数
2. 然后使用循环处理
3. 最后返回结果"""
    
    result = remove_thinking_content(text, "MySFTModel")
    assert result == text, "Should keep original if no thinking indicators"
    print("✅ SFT without thinking: PASS")
    return True


def test_normal_answer_with_ambiguous_separator():
    """Test normal answer that has separator but no thinking indicators"""
    text = """这是一个完整的技术方案。

首先，系统需要处理用户输入。

然后，进行数据验证。

最后，返回处理结果。

这是一个完整的技术方案。

首先，系统需要处理用户输入。

然后，进行数据验证。

最后，返回处理结果。"""
    
    result = remove_thinking_content(text, "NormalModel")
    # Should keep original because first part doesn't have thinking indicators
    assert "这是一个完整的技术方案" in result, "Should keep original"
    print("✅ Normal answer with separator: PASS")
    return True


if __name__ == "__main__":
    print("Testing remove_thinking_content function...\n")
    
    all_pass = True
    all_pass &= test_qwen_with_thinking()
    all_pass &= test_qwen_without_separator()
    all_pass &= test_sft_with_thinking()
    all_pass &= test_sft_without_thinking()
    all_pass &= test_normal_answer_with_ambiguous_separator()
    
    if all_pass:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
