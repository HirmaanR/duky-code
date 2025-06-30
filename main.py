#!/usr/bin/env python3
"""
Ducky AI Assistant - A terminal-based AI coding assistant
Similar to Claude Code but with a duck theme
"""

import os
import sys
import json
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
import re
from openai import OpenAI

# Initialize Rich console
console = Console()

# AI Configuration Constants
AI_BASE_URL = "https://api.aimlapi.com/v1"
AI_MODEL = "google/gemma-3-27b-it"
AI_MAX_TOKENS = 2000
AI_TEMPERATURE = 0.7

# Color theme - Professional Duck
COLORS = {
    'primary': '#1E3A8A',      # Duck blue
    'accent': '#F59E0B',       # Golden yellow
    'success': '#10B981',      # Emerald
    'error': '#EF4444',        # Rose
    'warning': '#F59E0B',      # Amber
    'muted': '#64748B',        # Gray-blue
    'code_bg': '#1F2937'       # Dark gray
}

# Ducky ASCII Art
DUCKY_LOGO = """

██████╗ ██╗   ██╗██╗  ██╗██╗   ██╗
██╔══██╗██║   ██║██║ ██╔╝╚██╗ ██╔╝
██║  ██║██║   ██║█████╔╝  ╚████╔╝ 
██║  ██║██║   ██║██╔═██╗   ╚██╔╝  
██████╔╝╚██████╔╝██║  ██╗   ██║   
╚═════╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
                                  
 ██████╗ ██████╗ ██████╗ ███████╗ 
██╔════╝██╔═══██╗██╔══██╗██╔════╝ 
██║     ██║   ██║██║  ██║█████╗   
██║     ██║   ██║██║  ██║██╔══╝   
╚██████╗╚██████╔╝██████╔╝███████╗ 
 ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝ 
                                  
"""

class DuckyConfig:
    """Configuration management for Ducky AI"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.ducky'
        self.config_file = self.config_dir / 'config.json'
        self.config_dir.mkdir(exist_ok=True)
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError:
            return False
    
    def get_api_key(self):
        """Get stored API key"""
        return self.config.get('api_key')
    
    def set_api_key(self, key):
        """Set and save API key"""
        self.config['api_key'] = key
        return self.save_config()

class DuckyAI:
    """Main Ducky AI assistant class"""
    
    def __init__(self):
        self.config = DuckyConfig()
        self.api_key = None
        self.client = None
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_welcome(self):
        """Display welcome message and logo"""
        self.clear_screen()
        
        # Display logo with styling
        logo_text = Text(DUCKY_LOGO, style=COLORS['accent'])
        console.print(logo_text, justify="center")
        
        # Welcome message
        welcome_panel = Panel(
            Text("Welcome to Ducky AI! 🦆\nYour intelligent coding companion", 
                 style="bold", justify="center"),
            border_style=COLORS['primary'],
            padding=(1, 2)
        )
        console.print(welcome_panel)
        console.print()
    
    def verify_api_key(self, api_key):
        """Verify API key by sending a test request"""
        test_prompt = "You are a helpful assistant for programmers. Please respond with 'API key verified successfully' if you receive this message."
        
        try:
            # Initialize OpenAI client with the provided key
            test_client = OpenAI(
                api_key=api_key,
                base_url=AI_BASE_URL
            )
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("🦆 Verifying API key...", total=None)
                
                response = test_client.chat.completions.create(
                    model=AI_MODEL,
                    messages=[{'role': 'user', 'content': test_prompt}],
                    max_tokens=50,
                    temperature=0.3
                )
                
                ai_response = response.choices[0].message.content
                return True, ai_response
                    
        except Exception as e:
            return False, f"Verification failed: {str(e)}"
    
    def setup_api_key(self):
        """Handle API key setup process"""
        console.print(Panel(
            "🔑 API Key Setup Required\n\n"
            "Ducky needs an OpenAI API key to function.\n"
            "You can get one from: https://platform.openai.com/api-keys\n\n"
            "Your key will be stored securely in ~/.ducky/config.json",
            title="Setup Required",
            border_style=COLORS['warning']
        ))
        console.print()
        
        while True:
            api_key = Prompt.ask(
                "🦆 Please enter your OpenAI API key",
                password=True,
                console=console
            )
            
            if not api_key or len(api_key.strip()) < 10:
                console.print("❌ Invalid API key format. Please try again.", style=COLORS['error'])
                continue
            
            # Verify the key
            success, message = self.verify_api_key(api_key)
            
            if success:
                if self.config.set_api_key(api_key):
                    console.print(f"✅ API key verified and saved!", style=COLORS['success'])
                    console.print(Panel(message, border_style=COLORS['success']))
                    self.api_key = api_key
                    # Initialize the OpenAI client
                    self.client = OpenAI(
                        api_key=api_key,
                        base_url=AI_BASE_URL
                    )
                    time.sleep(2)
                    return True
                else:
                    console.print("❌ Failed to save API key", style=COLORS['error'])
            else:
                console.print(f"❌ {message}", style=COLORS['error'])
                retry = Prompt.ask("Try again? (y/n)", default="y")
                if retry.lower() != 'y':
                    return False
    
    def send_message(self, message):
        """Send message to AI and get response"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("🦆 Ducky is thinking...", total=None)
                
                response = self.client.chat.completions.create(
                    model=AI_MODEL,
                    messages=[
                        {
                            'role': 'system', 
                            'content': 'You are Ducky, a helpful AI assistant specialized in helping programmers. Provide clear, concise responses with code examples when appropriate.'
                        },
                        {'role': 'user', 'content': message}
                    ],
                    max_tokens=AI_MAX_TOKENS,
                    temperature=AI_TEMPERATURE
                )
            
            ai_response = response.choices[0].message.content
            return True, ai_response
                
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def format_response(self, response_text):
        """Format and display AI response with proper styling"""
        console.print()
        
        # Response header
        header = Panel(
            Text("🦆 Ducky's Response", style="bold"),
            border_style=COLORS['accent'],
        )
        console.print(header)
        
        # Check if response contains code blocks
        code_pattern = r'```(\w+)?\n(.*?)\n```'
        parts = re.split(code_pattern, response_text, flags=re.DOTALL)
        
        for i, part in enumerate(parts):
            if i % 3 == 0:  # Regular text
                if part.strip():
                    # Use Markdown for formatting
                    console.print(Markdown(part.strip()))
            elif i % 3 == 1:  # Language identifier
                continue
            else:  # Code block
                language = parts[i-1] if parts[i-1] else "text"
                syntax = Syntax(part.strip(), language, theme="monokai", background_color=COLORS['code_bg'])
                console.print(Panel(syntax, border_style=COLORS['muted']))
                
                # Show copy hint
                console.print(f"💡 Tip: You can copy this {language} code", style=COLORS['muted'])
        
        console.print()
    
    def main_loop(self):
        """Main interaction loop"""
        console.print(Panel(
            "🦆 Ducky is ready! Type your programming questions or requests.\n"
            "Commands: 'exit' or 'quit' to leave, 'clear' to clear screen",
            border_style=COLORS['primary']
        ))
        
        while True:
            try:
                console.print()
                user_input = Prompt.ask(
                    "[bold]🦆 You[/bold]",
                    console=console
                ).strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    console.print("👋 Goodbye! Happy coding!", style=COLORS['accent'])
                    break
                elif user_input.lower() == 'clear':
                    self.show_welcome()
                    continue
                
                # Send message to AI
                success, response = self.send_message(user_input)
                
                if success:
                    self.format_response(response)
                else:
                    console.print(f"❌ Error: {response}", style=COLORS['error'])
                    
            except KeyboardInterrupt:
                console.print("\n\n👋 Goodbye! Happy coding!", style=COLORS['accent'])
                break
            except Exception as e:
                console.print(f"❌ Unexpected error: {str(e)}", style=COLORS['error'])
    
    def run(self):
        """Main entry point"""
        # Clear screen immediately when program starts
        self.clear_screen()
        self.show_welcome()
        
        # Check for existing API key
        self.api_key = self.config.get_api_key()
        
        if not self.api_key:
            if not self.setup_api_key():
                console.print("❌ Setup cancelled. Exiting...", style=COLORS['error'])
                return
        else:
            # Initialize client with existing key
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=AI_BASE_URL
            )
            console.print("✅ API key found! Ducky is ready.", style=COLORS['success'])
            time.sleep(1)
        
        # Clear screen and start main loop
        self.clear_screen()
        self.show_welcome()
        self.main_loop()

def main():
    """Entry point function"""
    try:
        ducky = DuckyAI()
        ducky.run()
    except Exception as e:
        console.print(f"❌ Fatal error: {str(e)}", style="red")
        sys.exit(1)

if __name__ == "__main__":
    main()
