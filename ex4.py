import importlib
import inspect
from pathlib import Path
from typing import Protocol, Any, Dict, List, Optional
import asyncio

# 1. Define the plugin interface
class TextAnalyzer(Protocol):
    name: str = "Unnamed Plugin"
    version: str = "0.1"
    description: str = "No description"

    def analyze(self, text: str) -> Dict[str, Any]:
        """Synchronous analysis"""
        ...

    async def analyze_async(self, text: str) -> Dict[str, Any]:
        """Asynchronous analysis"""
        ...

# 2. Plugin Manager
class PluginManager:
    def __init__(self):
        self.plugins: List[TextAnalyzer] = []

    def load_plugins(self, plugin_dir: str = "plugins"):
        """Load all plugins from a directory"""
        plugin_files = Path(plugin_dir).glob("*.py")
        
        for plugin_file in plugin_files:
            try:
                module = importlib.import_module(f"{plugin_dir}.{plugin_file.stem}")
                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and obj.__module__ == module.__name__
                        and not inspect.isabstract(obj)
                    ):
                        plugin = obj()
                        if self._validate_plugin(plugin):
                            self.plugins.append(plugin)
            except Exception as e:
                print(f"Failed to load {plugin_file}: {e}")

    def _validate_plugin(self, plugin: Any) -> bool:
        """Check if plugin implements required methods"""
        required = {"analyze", "analyze_async", "name", "version"}
        return all(hasattr(plugin, attr) for attr in required)

    async def run_analysis(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Run all analyzers on text"""
        results = {}
        
        # Run synchronous analyzers
        for plugin in self.plugins:
            try:
                results[plugin.name] = plugin.analyze(text)
            except Exception as e:
                results[plugin.name] = {"error": str(e)}
        
        # Run asynchronous analyzers
        async_tasks = [plugin.analyze_async(text) for plugin in self.plugins]
        async_results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        for plugin, result in zip(self.plugins, async_results):
            if not isinstance(result, Exception):
                results[plugin.name]["async"] = result
            else:
                results[plugin.name]["async_error"] = str(result)
        
        return results

# 3. Example Plugins (would normally be in separate files)
class WordCounter:
    name = "Word Counter"
    version = "1.0"
    description = "Counts words and characters"

    def analyze(self, text: str) -> Dict[str, Any]:
        words = len(text.split())
        chars = len(text)
        return {"words": words, "characters": chars}

    async def analyze_async(self, text: str) -> Dict[str, Any]:
        return self.analyze(text)

class SentimentAnalyzer:
    name = "Sentiment Analyzer"
    version = "1.1"
    description = "Basic sentiment analysis"

    def analyze(self, text: str) -> Dict[str, Any]:
        positive_words = {"good", "great", "awesome"}
        negative_words = {"bad", "terrible", "awful"}
        
        score = 0
        for word in text.lower().split():
            if word in positive_words:
                score += 1
            elif word in negative_words:
                score -= 1
        return {"sentiment_score": score}

    async def analyze_async(self, text: str) -> Dict[str, Any]:
        return self.analyze(text)

class LanguageDetector:
    name = "Language Detector"
    version = "1.2"
    description = "Detects common words"

    def analyze(self, text: str) -> Dict[str, Any]:
        english_words = {"the", "and", "is"}
        spanish_words = {"el", "la", "y"}
        
        text_words = set(text.lower().split())
        return {
            "english_words": len(text_words & english_words),
            "spanish_words": len(text_words & spanish_words)
        }

    async def analyze_async(self, text: str) -> Dict[str, Any]:
        return self.analyze(text)

# Example Usage
if __name__ == "__main__":
    # Create and configure manager
    manager = PluginManager()
    
    # Normally these would be autoloaded from plugins/
    manager.plugins = [WordCounter(), SentimentAnalyzer(), LanguageDetector()]
    
    # Run analysis
    text = "Python is great but sometimes terrible"
    results = asyncio.run(manager.run_analysis(text))
    
    # Print results
    import pprint
    pprint.pprint(results)
