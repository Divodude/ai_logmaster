"""
Global LLM Manager Singleton
Manages the instantiation and caching of the LLM based on configuration.
"""
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel

from ai_logmaster.config import get_config

class GlobalLLMManager:
    _instance = None
    _llm = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalLLMManager, cls).__new__(cls)
        return cls._instance

    def get_llm(self) -> Optional[BaseChatModel]:
        """
        Returns the singleton instance of the LLM. 
        Initializes it if not already initialized.
        """
        if self._llm is None:
            self.initialize_llm()
        return self._llm

    def initialize_llm(self) -> None:
        """
        Initializes the LLM based on the global configuration.
        Supports OpenAI, Groq, Anthropic, Google, and Nvidia out of the box.
        """
        config = get_config()
        ai_config = config.get_ai_config()

        provider = ai_config.get("provider", "openai").lower()
        model_name = ai_config.get("model", "")
        api_key = ai_config.get("api_key", "")
        temperature = ai_config.get("temperature", 0.1)
        max_tokens = ai_config.get("max_tokens", 1024)
        base_url = ai_config.get("base_url", "")

        try:
            if provider in ["openai", "nvidia"]:
                from langchain_openai import ChatOpenAI
                
                kwargs = {
                    "model": model_name,
                    "api_key": api_key,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                if base_url:
                    kwargs["base_url"] = base_url
                    
                self._llm = ChatOpenAI(**kwargs)
                print(f"[LLM_MANAGER] Initialized ChatOpenAI (provider: {provider})")
                
            elif provider == "groq":
                from langchain_groq import ChatGroq
                self._llm = ChatGroq(
                    model=model_name,
                    api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                print("[LLM_MANAGER] Initialized ChatGroq")
                
            elif provider == "anthropic":
                from langchain_anthropic import ChatAnthropic
                self._llm = ChatAnthropic(
                    model=model_name,
                    api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                print("[LLM_MANAGER] Initialized ChatAnthropic")
                
            elif provider == "google":
                from langchain_google_genai import ChatGoogleGenerativeAI
                self._llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                print("[LLM_MANAGER] Initialized ChatGoogleGenerativeAI")
                
            else:
                print(f"[LLM_MANAGER] Unsupported provider: {provider}")
                self._llm = None
                
        except ImportError as e:
            print(f"[LLM_MANAGER] Failed to import provider '{provider}': {e}")
            print(f"Please install the appropriate package (e.g., pip install langchain-{provider if provider != 'nvidia' else 'openai'})")
            self._llm = None
        except Exception as e:
            print(f"[LLM_MANAGER] Failed to initialize LLM for provider '{provider}': {e}")
            self._llm = None

    def set_llm(self, llm: BaseChatModel) -> None:
        """
        Allows manually overriding the global LLM instance.
        """
        self._llm = llm
