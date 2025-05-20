"""
Customization States Module for the Website Creator

This module defines all the states and transitions for the website customization flow,
providing a comprehensive state management system for template customization.
"""

# Basic state enum constants
STATES = {
    # Initial and completion states
    'IDLE': 'idle',                                 # Starting state before any interaction
    'COMPLETED': 'completed',                       # Final state after website generation
    
    # Primary content states
    'WAITING_FOR_COIN_NAME': 'waiting_for_coin_name', # Waiting for the name of the coin/project
    'WAITING_FOR_SLOGAN': 'waiting_for_slogan',     # Waiting for project slogan or tagline
    'WAITING_FOR_DESCRIPTION': 'waiting_for_description', # Waiting for detailed description
    
    # Visual customization states
    'WAITING_FOR_LOGO': 'waiting_for_logo',         # Waiting for logo upload
    'WAITING_FOR_THEME': 'waiting_for_theme',       # Waiting for theme selection
    'WAITING_FOR_COLOR_SCHEME': 'waiting_for_color_scheme', # Waiting for color selection
    
    # Social media states
    'WAITING_FOR_TELEGRAM': 'waiting_for_telegram', # Waiting for Telegram link
    'WAITING_FOR_TWITTER': 'waiting_for_twitter',   # Waiting for Twitter link
    'WAITING_FOR_DISCORD': 'waiting_for_discord',   # Waiting for Discord link
    'WAITING_FOR_MEDIUM': 'waiting_for_medium',     # Waiting for Medium link
    'WAITING_FOR_GITHUB': 'waiting_for_github',     # Waiting for GitHub link
    'WAITING_FOR_CUSTOM_SOCIAL': 'waiting_for_custom_social', # Waiting for custom social link
    
    # Tokenomics states
    'WAITING_FOR_SUPPLY': 'waiting_for_supply',     # Waiting for token supply info
    'WAITING_FOR_TAX_INFO': 'waiting_for_tax_info', # Waiting for token tax/fees info
    'WAITING_FOR_DISTRIBUTION': 'waiting_for_distribution', # Waiting for token distribution
    
    # Roadmap states
    'WAITING_FOR_ROADMAP': 'waiting_for_roadmap',   # Waiting for roadmap steps
    
    # Template-specific states
    'WAITING_FOR_TEMPLATE_SELECTION': 'waiting_for_template_selection', # Choosing template type
    'WAITING_FOR_SECTIONS_ORDER': 'waiting_for_sections_order', # Ordering sections
    
    # Meta states
    'WAITING_FOR_CONFIRMATION': 'waiting_for_confirmation', # Confirming all settings
    'WAITING_FOR_EDIT_CHOICE': 'waiting_for_edit_choice', # Selecting which field to edit
    'READY_TO_GENERATE': 'ready_to_generate',       # Ready to generate website
    'GENERATING': 'generating',                     # Website generation in progress
    
    # Hosting states
    'WAITING_FOR_HOSTING_CHOICE': 'waiting_for_hosting_choice', # Selecting hosting method
    'WAITING_FOR_DOMAIN': 'waiting_for_domain',     # Waiting for custom domain
    
    # Error and special states
    'ERROR': 'error',                               # Error occurred during customization
    'TIMEOUT': 'timeout'                            # Session timeout
}

# Define state transitions and valid next states
STATE_TRANSITIONS = {
    STATES['IDLE']: [
        STATES['WAITING_FOR_TEMPLATE_SELECTION']
    ],
    
    STATES['WAITING_FOR_TEMPLATE_SELECTION']: [
        STATES['WAITING_FOR_COIN_NAME']
    ],
    
    STATES['WAITING_FOR_COIN_NAME']: [
        STATES['WAITING_FOR_SLOGAN'],
        STATES['WAITING_FOR_DESCRIPTION'],
        STATES['WAITING_FOR_LOGO'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_SLOGAN']: [
        STATES['WAITING_FOR_DESCRIPTION'],
        STATES['WAITING_FOR_LOGO'],
        STATES['WAITING_FOR_THEME'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_DESCRIPTION']: [
        STATES['WAITING_FOR_LOGO'],
        STATES['WAITING_FOR_THEME'],
        STATES['WAITING_FOR_TELEGRAM'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_LOGO']: [
        STATES['WAITING_FOR_THEME'],
        STATES['WAITING_FOR_COLOR_SCHEME'],
        STATES['WAITING_FOR_TELEGRAM'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_THEME']: [
        STATES['WAITING_FOR_COLOR_SCHEME'],
        STATES['WAITING_FOR_TELEGRAM'],
        STATES['WAITING_FOR_TWITTER'],
        STATES['WAITING_FOR_DISCORD'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_COLOR_SCHEME']: [
        STATES['WAITING_FOR_TELEGRAM'],
        STATES['WAITING_FOR_TWITTER'],
        STATES['WAITING_FOR_DISCORD'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_TELEGRAM']: [
        STATES['WAITING_FOR_TWITTER'],
        STATES['WAITING_FOR_DISCORD'],
        STATES['WAITING_FOR_MEDIUM'],
        STATES['WAITING_FOR_SUPPLY'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_TWITTER']: [
        STATES['WAITING_FOR_DISCORD'],
        STATES['WAITING_FOR_MEDIUM'],
        STATES['WAITING_FOR_GITHUB'],
        STATES['WAITING_FOR_SUPPLY'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_DISCORD']: [
        STATES['WAITING_FOR_MEDIUM'],
        STATES['WAITING_FOR_GITHUB'],
        STATES['WAITING_FOR_CUSTOM_SOCIAL'],
        STATES['WAITING_FOR_SUPPLY'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_MEDIUM']: [
        STATES['WAITING_FOR_GITHUB'],
        STATES['WAITING_FOR_CUSTOM_SOCIAL'],
        STATES['WAITING_FOR_SUPPLY'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_GITHUB']: [
        STATES['WAITING_FOR_CUSTOM_SOCIAL'],
        STATES['WAITING_FOR_SUPPLY'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_CUSTOM_SOCIAL']: [
        STATES['WAITING_FOR_SUPPLY'],
        STATES['WAITING_FOR_TAX_INFO'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_SUPPLY']: [
        STATES['WAITING_FOR_TAX_INFO'],
        STATES['WAITING_FOR_DISTRIBUTION'],
        STATES['WAITING_FOR_ROADMAP'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_TAX_INFO']: [
        STATES['WAITING_FOR_DISTRIBUTION'],
        STATES['WAITING_FOR_ROADMAP'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_DISTRIBUTION']: [
        STATES['WAITING_FOR_ROADMAP'],
        STATES['WAITING_FOR_SECTIONS_ORDER'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_ROADMAP']: [
        STATES['WAITING_FOR_SECTIONS_ORDER'],
        STATES['WAITING_FOR_CONFIRMATION'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_SECTIONS_ORDER']: [
        STATES['WAITING_FOR_CONFIRMATION'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_CONFIRMATION']: [
        STATES['WAITING_FOR_EDIT_CHOICE'],
        STATES['READY_TO_GENERATE'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_EDIT_CHOICE']: [
        # Can go back to any of the input states
        STATES['WAITING_FOR_COIN_NAME'],
        STATES['WAITING_FOR_SLOGAN'],
        STATES['WAITING_FOR_DESCRIPTION'],
        STATES['WAITING_FOR_LOGO'],
        STATES['WAITING_FOR_THEME'],
        STATES['WAITING_FOR_COLOR_SCHEME'],
        STATES['WAITING_FOR_TELEGRAM'],
        STATES['WAITING_FOR_TWITTER'],
        STATES['WAITING_FOR_DISCORD'],
        STATES['WAITING_FOR_MEDIUM'],
        STATES['WAITING_FOR_GITHUB'],
        STATES['WAITING_FOR_CUSTOM_SOCIAL'],
        STATES['WAITING_FOR_SUPPLY'],
        STATES['WAITING_FOR_TAX_INFO'],
        STATES['WAITING_FOR_DISTRIBUTION'],
        STATES['WAITING_FOR_ROADMAP'],
        STATES['WAITING_FOR_SECTIONS_ORDER'],
        STATES['WAITING_FOR_CONFIRMATION'],
        STATES['ERROR']
    ],
    
    STATES['READY_TO_GENERATE']: [
        STATES['GENERATING'],
        STATES['WAITING_FOR_CONFIRMATION'],
        STATES['ERROR']
    ],
    
    STATES['GENERATING']: [
        STATES['WAITING_FOR_HOSTING_CHOICE'],
        STATES['COMPLETED'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_HOSTING_CHOICE']: [
        STATES['WAITING_FOR_DOMAIN'],
        STATES['COMPLETED'],
        STATES['ERROR']
    ],
    
    STATES['WAITING_FOR_DOMAIN']: [
        STATES['COMPLETED'],
        STATES['ERROR']
    ],
    
    STATES['COMPLETED']: [
        STATES['IDLE']  # Start over
    ],
    
    STATES['ERROR']: [
        STATES['IDLE'],  # Reset to beginning
        # Can also potentially go back to the state that caused the error
    ],
    
    STATES['TIMEOUT']: [
        STATES['IDLE']  # Reset after timeout
    ]
}

# Define required fields for each state
REQUIRED_FIELDS = {
    STATES['WAITING_FOR_COIN_NAME']: ['coin_name'],
    STATES['WAITING_FOR_SLOGAN']: ['slogan'],
    STATES['WAITING_FOR_DESCRIPTION']: ['description'],
    STATES['WAITING_FOR_LOGO']: ['logo_url'],
    STATES['WAITING_FOR_THEME']: ['theme'],
    STATES['WAITING_FOR_COLOR_SCHEME']: ['primary_color', 'secondary_color', 'accent_color'],
    STATES['WAITING_FOR_TELEGRAM']: ['telegram_url'],
    STATES['WAITING_FOR_TWITTER']: ['twitter_url'],
    STATES['WAITING_FOR_DISCORD']: ['discord_url'],
    STATES['WAITING_FOR_MEDIUM']: ['medium_url'],
    STATES['WAITING_FOR_GITHUB']: ['github_url'],
    STATES['WAITING_FOR_CUSTOM_SOCIAL']: ['custom_social_name', 'custom_social_url'],
    STATES['WAITING_FOR_SUPPLY']: ['total_supply'],
    STATES['WAITING_FOR_TAX_INFO']: ['buy_tax', 'sell_tax'],
    STATES['WAITING_FOR_DISTRIBUTION']: ['distribution'],
    STATES['WAITING_FOR_ROADMAP']: ['roadmap_phases'],
    STATES['WAITING_FOR_SECTIONS_ORDER']: ['sections_order'],
    STATES['WAITING_FOR_TEMPLATE_SELECTION']: ['template_id'],
    STATES['WAITING_FOR_HOSTING_CHOICE']: ['hosting_method'],
    STATES['WAITING_FOR_DOMAIN']: ['custom_domain']
}

# Define prompt messages for each state
STATE_PROMPTS = {
    STATES['IDLE']: "Welcome to the Website Creator! Let's build your custom website. Type /start to begin.",
    STATES['WAITING_FOR_TEMPLATE_SELECTION']: "Please select a template for your website:",
    STATES['WAITING_FOR_COIN_NAME']: "What's the name of your coin or project?",
    STATES['WAITING_FOR_SLOGAN']: "Enter a catchy slogan for your project (or type 'skip' to use a random one):",
    STATES['WAITING_FOR_DESCRIPTION']: "Please provide a brief description of your project (or type 'skip'):",
    STATES['WAITING_FOR_LOGO']: "Please upload a logo image (or type 'skip' to use a generated symbol):",
    STATES['WAITING_FOR_THEME']: "Select a theme for your website:",
    STATES['WAITING_FOR_COLOR_SCHEME']: "Choose a color scheme or provide custom colors:",
    STATES['WAITING_FOR_TELEGRAM']: "Enter your Telegram group link (or type 'skip'):",
    STATES['WAITING_FOR_TWITTER']: "Enter your Twitter profile link (or type 'skip'):",
    STATES['WAITING_FOR_DISCORD']: "Enter your Discord server link (or type 'skip'):",
    STATES['WAITING_FOR_MEDIUM']: "Enter your Medium profile link (or type 'skip'):",
    STATES['WAITING_FOR_GITHUB']: "Enter your GitHub repository link (or type 'skip'):",
    STATES['WAITING_FOR_CUSTOM_SOCIAL']: "Enter a custom social media name and link (or type 'skip'):",
    STATES['WAITING_FOR_SUPPLY']: "Enter the total supply for your token (or type 'skip' for a random value):",
    STATES['WAITING_FOR_TAX_INFO']: "Enter the buy and sell tax percentages (or type 'skip' for random values):",
    STATES['WAITING_FOR_DISTRIBUTION']: "Enter token distribution details (or type 'skip' for default values):",
    STATES['WAITING_FOR_ROADMAP']: "Enter roadmap milestones (or type 'skip' for a generated roadmap):",
    STATES['WAITING_FOR_SECTIONS_ORDER']: "Arrange the order of sections on your website:",
    STATES['WAITING_FOR_CONFIRMATION']: "Please review your website information and confirm or edit:",
    STATES['WAITING_FOR_EDIT_CHOICE']: "Which field would you like to edit?",
    STATES['READY_TO_GENERATE']: "Ready to generate your website. Send any message to continue.",
    STATES['GENERATING']: "Generating your website. Please wait...",
    STATES['WAITING_FOR_HOSTING_CHOICE']: "How would you like to host your website?",
    STATES['WAITING_FOR_DOMAIN']: "Enter a custom domain for your website (optional):",
    STATES['COMPLETED']: "Your website has been generated and is ready to view!",
    STATES['ERROR']: "An error occurred. Please try again or start over.",
    STATES['TIMEOUT']: "Your session has timed out. Please start over."
}

# Default data template (initial empty state)
DEFAULT_WEBSITE_DATA = {
    'template_id': None,
    'coin_name': None,
    'formatted_name': None,
    'symbol': None,
    'slogan': None,
    'description': None,
    'logo_url': None,
    'theme': None,
    'colors': {
        'primary': None,
        'secondary': None,
        'accent': None
    },
    'social_links': {
        'telegram': None,
        'twitter': None,
        'discord': None,
        'medium': None,
        'github': None,
        'custom': []
    },
    'tokenomics': {
        'total_supply': None,
        'buy_tax': None,
        'sell_tax': None,
        'burn': None,
        'redistribution': None,
        'liquidity': None,
        'marketing': None,
        'distribution': []
    },
    'roadmap': [],
    'sections_order': [
        'header',
        'about',
        'tokenomics',
        'roadmap',
        'community'
    ],
    'hosting': {
        'method': None,
        'custom_domain': None
    },
    'site_hash': None,
    'urls': {
        'raw_url': None,
        'preview_url': None,
        'repo_url': None
    }
}

# State management class
class CustomizationStateManager:
    """
    Manages the state transitions and data for the website customization flow.
    
    This class handles:
    - Current state tracking
    - Valid state transitions
    - Required field validation
    - Default data initialization
    - State-specific prompt messages
    """
    
    def __init__(self, user_id):
        """Initialize a new state manager for a user."""
        self.user_id = user_id
        self.current_state = STATES['IDLE']
        self.website_data = DEFAULT_WEBSITE_DATA.copy()
        self.error_message = None
    
    def get_current_state(self):
        """Get the current state."""
        return self.current_state
    
    def get_prompt(self):
        """Get the prompt message for the current state."""
        return STATE_PROMPTS.get(self.current_state, "")
    
    def get_required_fields(self):
        """Get the required fields for the current state."""
        return REQUIRED_FIELDS.get(self.current_state, [])
    
    def can_transition_to(self, new_state):
        """Check if a transition to the specified state is valid."""
        # Special case for initial transitions
        if self.current_state == STATES['IDLE'] and new_state == STATES['WAITING_FOR_TEMPLATE_SELECTION']:
            return True
            
        valid_transitions = STATE_TRANSITIONS.get(self.current_state, [])
        return new_state in valid_transitions
    
    def transition_to(self, new_state):
        """
        Attempt to transition to a new state.
        
        Returns:
            bool: True if transition was successful, False otherwise
        """
        # Allow forcing to template selection or generation states from any state
        # This is needed for AI-driven flows
        if (new_state == STATES['WAITING_FOR_TEMPLATE_SELECTION'] or 
            new_state == STATES['READY_TO_GENERATE'] or
            new_state == STATES['GENERATING']):
            self.current_state = new_state
            return True
            
        if self.can_transition_to(new_state):
            self.current_state = new_state
            return True
        
        # If transition fails, log error but allow it to proceed anyway
        # This makes the AI-driven flow more resilient
        self.error_message = f"Warning: Unusual state transition from {self.current_state} to {new_state}"
        self.current_state = new_state
        return True
    
    def update_data(self, field, value):
        """
        Update a field in the website data.
        
        Args:
            field: The field to update (can be a dot-notation path like 'colors.primary')
            value: The value to set
            
        Returns:
            bool: True if the update was successful, False otherwise
        """
        try:
            if '.' in field:
                # Handle nested fields
                parts = field.split('.')
                current = self.website_data
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                # Handle top-level fields
                self.website_data[field] = value
            return True
        except Exception as e:
            self.error_message = f"Error updating field {field}: {str(e)}"
            return False
    
    def validate_current_state(self):
        """
        Validate that all required fields for the current state are filled.
        
        Returns:
            bool: True if all required fields are filled, False otherwise
        """
        required_fields = self.get_required_fields()
        for field in required_fields:
            # Handle nested fields
            if '.' in field:
                parts = field.split('.')
                current = self.website_data
                valid = True
                for part in parts:
                    if part not in current or current[part] is None:
                        valid = False
                        break
                    current = current[part]
                if not valid:
                    self.error_message = f"Missing required field: {field}"
                    return False
            # Handle top-level fields
            elif field not in self.website_data or self.website_data[field] is None:
                self.error_message = f"Missing required field: {field}"
                return False
        return True
    
    def reset(self):
        """Reset to initial state."""
        self.current_state = STATES['IDLE']
        self.website_data = DEFAULT_WEBSITE_DATA.copy()
        self.error_message = None
    
    def get_error(self):
        """Get the last error message."""
        return self.error_message
    
    def get_website_data(self):
        """Get the current website data."""
        return self.website_data