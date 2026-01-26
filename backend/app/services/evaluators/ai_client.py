"""
Gemini API client for AI evaluation
Supports both Gemini (development) and Claude (production)
"""
import os
from typing import Dict, List, Optional
from enum import Enum


class AIProvider(Enum):
    """AI provider options"""
    GEMINI = "gemini"
    CLAUDE = "claude"


class AIEvaluator:
    """Unified AI evaluator that works with Gemini or Claude"""
    
    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        claude_api_key: Optional[str] = None,
        use_claude: bool = False
    ):
        """
        Initialize AI evaluator
        
        Args:
            gemini_api_key: Gemini API key
            claude_api_key: Claude API key
            use_claude: If True, use Claude; otherwise use Gemini
        """
        self.use_claude = use_claude
        self.provider = AIProvider.CLAUDE if use_claude else AIProvider.GEMINI
        
        if use_claude:
            self.api_key = claude_api_key
            self._init_claude()
        else:
            self.api_key = gemini_api_key
            self._init_gemini()
    
    def _init_gemini(self):
        """Initialize Gemini API"""
        try:
            import google.generativeai as genai
            
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                self.client = self.model
            else:
                print("Warning: Gemini API key not provided")
                self.client = None
        except ImportError:
            print("Warning: google-generativeai not installed")
            self.client = None
        except Exception as e:
            print(f"Warning: Could not initialize Gemini: {e}")
            self.client = None
    
    def _init_claude(self):
        """Initialize Claude API"""
        try:
            import anthropic
            
            if self.api_key:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            else:
                print("Warning: Claude API key not provided")
                self.client = None
        except ImportError:
            print("Warning: anthropic not installed")
            self.client = None
        except Exception as e:
            print(f"Warning: Could not initialize Claude: {e}")
            self.client = None
    
    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        Generate response from AI
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens in response
            
        Returns:
            AI response text
        """
        if not self.client:
            return self._mock_response(prompt)
        
        try:
            if self.provider == AIProvider.GEMINI:
                response = self.client.generate_content(prompt)
                return response.text
            else:  # Claude
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return message.content[0].text
        except Exception as e:
            print(f"AI generation error: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """Mock response for development/testing"""
        return """
[Mock AI Response]
Marks: 7/10
Feedback: Student demonstrates good understanding of core concepts.
Strengths: Clear explanation, correct approach
Improvements: Could provide more detailed examples
"""


# Convenience function
def create_ai_evaluator(
    gemini_api_key: Optional[str] = None,
    claude_api_key: Optional[str] = None,
    use_claude: bool = False
) -> AIEvaluator:
    """
    Create AI evaluator instance
    
    Args:
        gemini_api_key: Gemini API key
        claude_api_key: Claude API key
        use_claude: Whether to use Claude instead of Gemini
        
    Returns:
        AIEvaluator instance
    """
    return AIEvaluator(gemini_api_key, claude_api_key, use_claude)
