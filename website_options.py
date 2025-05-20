"""
Website generation options for the Memecoin Website Generator.
This file contains thousands of combinations for generating unique websites.
"""

import random

# ==============================
# COLOR THEMES - 50 combinations
# ==============================
THEMES = [
    # Vibrant themes
    {"primary": "#FF6B6B", "secondary": "#4ECDC4", "accent": "#FFE66D", "name": "Candy Pop"},
    {"primary": "#6B5B95", "secondary": "#FFA500", "accent": "#88B04B", "name": "Royal Citrus"},
    {"primary": "#00A4CCFF", "secondary": "#F95700FF", "accent": "#ADEFD1FF", "name": "Ocean Flame"},
    {"primary": "#00539CFF", "secondary": "#EEA47FFF", "accent": "#D198C5FF", "name": "Azure Dream"},
    {"primary": "#2C5F2D", "secondary": "#97BC62FF", "accent": "#FE5F55", "name": "Forest Fire"},
    {"primary": "#990011FF", "secondary": "#FCF6F5FF", "accent": "#8AAAE5", "name": "Blood Moon"},
    
    # Neon themes
    {"primary": "#0D0221", "secondary": "#0F2557", "accent": "#00DFFC", "name": "Cyber Neon"},
    {"primary": "#150050", "secondary": "#3F0071", "accent": "#FB2576", "name": "Neon Nights"},
    {"primary": "#292C6D", "secondary": "#15133C", "accent": "#EC994B", "name": "Digital Sunset"},
    {"primary": "#561C24", "secondary": "#6D213C", "accent": "#FE346E", "name": "Neon Rose"},
    {"primary": "#1F2833", "secondary": "#0B0C10", "accent": "#66FCF1", "name": "Tron Legacy"},
    {"primary": "#240046", "secondary": "#3C096C", "accent": "#5A189A", "name": "Ultraviolet"},
    
    # Pastels
    {"primary": "#FFCAD4", "secondary": "#F4ACB7", "accent": "#9D8189", "name": "Cotton Candy"},
    {"primary": "#CDEDF6", "secondary": "#B4CDE6", "accent": "#6AABD2", "name": "Pastel Ocean"},
    {"primary": "#D7F9FF", "secondary": "#D1D1F5", "accent": "#B8BEEF", "name": "Lavender Sky"},
    {"primary": "#E8F6EF", "secondary": "#B8DFD8", "accent": "#FFA4B6", "name": "Mint & Rose"},
    {"primary": "#EDDCD2", "secondary": "#DBD0C0", "accent": "#FECDAA", "name": "Desert Sand"},
    {"primary": "#FFCB77", "secondary": "#FEF9EF", "accent": "#FF9F1C", "name": "Golden Hour"},
    
    # Dark themes
    {"primary": "#0A0908", "secondary": "#22333B", "accent": "#F2A365", "name": "Midnight Gold"},
    {"primary": "#10002B", "secondary": "#240046", "accent": "#E0AAFF", "name": "Deep Purple"},
    {"primary": "#1A1A2E", "secondary": "#16213E", "accent": "#0F3460", "name": "Midnight Blue"},
    {"primary": "#252422", "secondary": "#403D39", "accent": "#EB5E28", "name": "Charcoal Fire"},
    {"primary": "#151515", "secondary": "#301B3F", "accent": "#3FC1C9", "name": "Dark Aqua"},
    {"primary": "#222831", "secondary": "#393E46", "accent": "#FFD369", "name": "Dark Amber"},
    
    # Gradients
    {"primary": "linear-gradient(135deg, #667eea, #764ba2)", "secondary": "#160A40", "accent": "#FFC44D", "name": "Purple Haze"},
    {"primary": "linear-gradient(135deg, #ff9a9e, #fad0c4)", "secondary": "#FF9AA2", "accent": "#191919", "name": "Soft Peach"},
    {"primary": "linear-gradient(135deg, #2af598, #009efd)", "secondary": "#1E5128", "accent": "#FF5C58", "name": "Ocean Mint"},
    {"primary": "linear-gradient(135deg, #f5f7fa, #c3cfe2)", "secondary": "#424874", "accent": "#F86624", "name": "Silver Lining"},
    {"primary": "linear-gradient(135deg, #5ee7df, #b490ca)", "secondary": "#3B1C32", "accent": "#FE7E6D", "name": "Mermaid Lagoon"},
    {"primary": "linear-gradient(135deg, #d9afd9, #97d9e1)", "secondary": "#5C374C", "accent": "#CCA43B", "name": "Silk Blend"},
    
    # Space themes
    {"primary": "#0F044C", "secondary": "#141E61", "accent": "#787A91", "name": "Cosmic Blue"},
    {"primary": "#040D12", "secondary": "#183D3D", "accent": "#5C8374", "name": "Deep Space"},
    {"primary": "#1E1E1E", "secondary": "#252A34", "accent": "#FF2E63", "name": "Cosmic Red"},
    {"primary": "#23120B", "secondary": "#925822", "accent": "#FFA931", "name": "Jupiter Rising"},
    {"primary": "#201335", "secondary": "#3B2347", "accent": "#719FB0", "name": "Nebula Dust"},
    {"primary": "#002642", "secondary": "#840032", "accent": "#E59500", "name": "Galactic Empire"},
    
    # Modern minimal
    {"primary": "#F8F9FA", "secondary": "#E9ECEF", "accent": "#212529", "name": "Clean Minimal"},
    {"primary": "#FFFFFF", "secondary": "#F6F6F6", "accent": "#1B262C", "name": "Pure White"},
    {"primary": "#E6E8E6", "secondary": "#CED0CE", "accent": "#9FB1BC", "name": "Gentle Gray"},
    {"primary": "#ECF2F9", "secondary": "#D4E5F9", "accent": "#E26D5C", "name": "Light Coral"},
    {"primary": "#EEF0F2", "secondary": "#D8DDE2", "accent": "#59D2FE", "name": "Nordic Blue"},
    {"primary": "#F5F5F5", "secondary": "#E5E5E5", "accent": "#00B2CA", "name": "Minimal Teal"},
    
    # Branded themes
    {"primary": "#4267B2", "secondary": "#898F9C", "accent": "#FFFFFF", "name": "Social Blue"},
    {"primary": "#1DA1F2", "secondary": "#14171A", "accent": "#FFFFFF", "name": "Tweet Blue"},
    {"primary": "#E1306C", "secondary": "#405DE6", "accent": "#FFDC80", "name": "Social Gradient"},
    {"primary": "#25D366", "secondary": "#128C7E", "accent": "#075E54", "name": "Message Green"},
    {"primary": "#FF4500", "secondary": "#FF8717", "accent": "#FFB000", "name": "Crypto Orange"},
    {"primary": "#7289DA", "secondary": "#424549", "accent": "#FFFFFF", "name": "Chat Theme"}
]

# =====================================
# SLOGAN TEMPLATES - 50+ combinations
# =====================================
SLOGAN_TEMPLATES = [
    # Classic crypto slogans
    "To The Moon! 🚀",
    "The Next 1000x Gem 💎",
    "Community-Driven Revolution 🔥",
    "The Future of Decentralized Memes 🌐",
    "Join The Movement! 💪",
    "Bark at The Moon 🐕",
    "Better Than Bitcoin? Maybe! 👀",
    "Elon Would Approve 👍",
    "Deflationary Tokenomics 📉",
    
    # Meme-focused slogans
    "Much Wow. Very Token. 🐕",
    "Memes + Crypto = 💰",
    "The Internet's Favorite Token 💻",
    "Not Just a Meme, a Movement 🚀",
    "The King of Meme Coins 👑",
    "When Memes Meet Money 💸",
    "Powered by Memes, Backed by Community 🤝",
    "Turning Memes into Dreams 💭",
    "The Ultimate Meme Money Machine 🏦",
    
    # Growth-focused slogans
    "1000x Your Investment Potential 📈",
    "From Zero to Moon in Record Time 🚀",
    "Growing Faster Than Any Other Token 📊",
    "Multiply Your Wealth With Memes 💰",
    "Exponential Growth Incoming 📈",
    "The Fastest Growing Token of {YEAR} 🏆",
    "Making Millionaires Daily 💵",
    "Stealth Launch, Rocket Growth 🚀",
    "The Next Crypto Unicorn 🦄",
    
    # Community-focused slogans
    "Built By The Community, For The Community 🤝",
    "Join {NUMBER}+ Holders Worldwide 🌍",
    "We're All Going to Make It 🚀",
    "Not a Token, a Family 👨‍👩‍👧‍👦",
    "The Friendliest Community in Crypto 😊",
    "Power to the HODLers 💪",
    "Where Memes Create Dreams 💭",
    "The People's Coin 👥",
    "Diamond Hands Only 💎🙌",
    
    # Future-focused slogans
    "The Future of Finance is Fun 🎮",
    "Revolutionizing DeFi One Meme at a Time 🌐",
    "Tomorrow's Currency, Today 📱",
    "Building the Future of Web3 🕸️",
    "The Token That Time Travels ⏰",
    "Ahead of the Curve 📈",
    "The Next Generation of Crypto 🔮",
    "Your Ticket to the Metaverse 🎫",
    "Pioneering Crypto Innovation 🧪",
    
    # Exclusive feeling slogans
    "Don't Miss Out This Time 😉",
    "The Only Token You'll Ever Need 💯",
    "Limited Supply, Unlimited Potential 🚀",
    "The VIP of Crypto 🎭",
    "Early Birds Get The Gains 🐦",
    "The Token Everyone Is Talking About 🗣️",
    "Get In Before It's Too Late ⏰",
    "The Hottest Token of {YEAR} 🔥",
    "Your Neighbors Will Be Jealous 😎"
]

# Fill in templates with current year and random numbers
def get_random_slogan():
    import datetime
    current_year = datetime.datetime.now().year
    slogan = random.choice(SLOGAN_TEMPLATES)
    
    if "{YEAR}" in slogan:
        slogan = slogan.replace("{YEAR}", str(current_year))
    
    if "{NUMBER}" in slogan:
        random_number = random.choice([10000, 25000, 50000, 100000, 250000, 500000, 1000000])
        slogan = slogan.replace("{NUMBER}", f"{random_number:,}")
        
    return slogan

# ==============================
# TOKENOMICS - 1000+ combinations
# ==============================
def generate_tokenomics():
    """Generate random but realistic tokenomics"""
    # Generate random total supply
    supply_options = [
        "1,000,000,000",       # 1 billion
        "10,000,000,000",      # 10 billion
        "100,000,000,000",     # 100 billion
        "1,000,000,000,000",   # 1 trillion
        "10,000,000,000,000",  # 10 trillion
        "100,000,000,000,000", # 100 trillion
        "1,000,000,000,000,000" # 1 quadrillion
    ]
    
    # Special meme numbers
    special_supplies = [
        "420,690,000,000",
        "69,420,000,000,000",
        "1,337,000,000,000",
        "42,069,000,000,000",
        "69,000,000,000,000"
    ]
    
    # 10% chance of special meme number
    if random.random() < 0.1:
        total_supply = random.choice(special_supplies)
    else:
        total_supply = random.choice(supply_options)
    
    # Generate distribution percentages
    # Let's create balanced tokenomics that add up to a reasonable amount (typically <50%)
    burn_pct = round(random.uniform(1, 10), 1)
    redistribution_pct = round(random.uniform(1, 7), 1)
    liquidity_pct = round(random.uniform(2, 10), 1)
    
    # 70% chance to have marketing
    if random.random() < 0.7:
        marketing_pct = round(random.uniform(1, 8), 1)
    else:
        marketing_pct = None
    
    # 30% chance to have team allocation
    if random.random() < 0.3:
        team_pct = round(random.uniform(1, 5), 1)
    else:
        team_pct = None
    
    # 20% chance to have special treasury/fund
    if random.random() < 0.2:
        treasury_pct = round(random.uniform(1, 5), 1)
        treasury_name = random.choice(["Treasury", "Development Fund", "Ecosystem Fund", "Community Fund"])
    else:
        treasury_pct = None
        treasury_name = None
    
    # Build tokenomics dictionary
    tokenomics = {
        "total_supply": total_supply,
        "burn": f"{burn_pct}%",
        "redistribution": f"{redistribution_pct}%",
        "liquidity": f"{liquidity_pct}%"
    }
    
    # Add optional components
    if marketing_pct:
        tokenomics["marketing"] = f"{marketing_pct}%"
        
    if team_pct:
        tokenomics["team"] = f"{team_pct}%"
        
    if treasury_pct and treasury_name:
        tokenomics[treasury_name.lower()] = f"{treasury_pct}%"
    
    return tokenomics

# ==============================
# ROADMAP - 1000+ combinations
# ==============================
ROADMAP_ITEMS = {
    "Phase 1 (Launch)": [
        "Website Launch",
        "Social Media Creation",
        "Community Building",
        "Token Launch",
        "Initial Marketing Push",
        "CoinGecko Listing",
        "CoinMarketCap Listing",
        "Whitepaper Release",
        "First Community AMA",
        "Smart Contract Audit",
        "Team Expansion",
        "Telegram Community Growth"
    ],
    
    "Phase 2 (Growth)": [
        "1,000 Holders Milestone",
        "5,000 Holders Milestone",
        "10,000 Holders Milestone",
        "MemeCoin Partnerships",
        "NFT Collection Launch",
        "Trending on Twitter",
        "Community Contests",
        "DApp Development",
        "Influencer Marketing",
        "Merchandise Store",
        "Dashboard Launch",
        "Enhanced Tokenomics"
    ],
    
    "Phase 3 (Expansion)": [
        "50,000 Holders Milestone",
        "100,000 Holders Milestone",
        "Major Exchange Listings",
        "Mobile App Development",
        "Mainstream Media Coverage",
        "Celebrity Endorsements",
        "Global Marketing Campaign",
        "Staking Platform Launch",
        "Cross-Chain Expansion",
        "DAO Implementation",
        "Metaverse Integration",
        "Real-World Partnerships"
    ],
    
    "Phase 4 (Maturity)": [
        "1 Million Holders Milestone",
        "Meme DEX Launch",
        "Meme Launchpad Platform",
        "NFT Marketplace Integration",
        "Global Adoption Initiative",
        "Educational Content Platform",
        "Developer Grants Program",
        "Enterprise Partnerships",
        "Charitable Foundation",
        "Real-World Use Cases",
        "Governance System",
        "Advanced DeFi Products"
    ]
}

def generate_roadmap():
    """Generate a unique roadmap with items from each phase"""
    roadmap = []
    
    # For each phase, select 3-5 random items
    for phase, items in ROADMAP_ITEMS.items():
        num_items = random.randint(3, 5)
        phase_items = random.sample(items, num_items)
        roadmap.append(phase_items)
    
    return roadmap

# ==============================
# EMOJI SETS - For dynamic styling
# ==============================
EMOJI_SETS = [
    ["🚀", "💎", "🔥", "💰", "🌙"],  # Classic crypto
    ["🐕", "🐶", "🦴", "🌭", "🐾"],   # Dog theme
    ["🐱", "😺", "🐟", "🧶", "🐭"],   # Cat theme
    ["🦊", "🦝", "🐺", "🌲", "🍂"],   # Fox theme
    ["🐸", "☕", "🍵", "🧠", "👑"],    # Frog theme
    ["🦍", "🍌", "🦧", "🌴", "🥥"],   # Ape theme
    ["👽", "🛸", "✨", "🌌", "🪐"],    # Alien theme
    ["🤖", "⚙️", "🔋", "💻", "🔌"],    # Robot theme
    ["🧙", "✨", "🔮", "📜", "⚡"],     # Wizard theme
    ["🏴‍☠️", "🦜", "⚓", "🏝️", "💰"],   # Pirate theme
    ["🍕", "🍔", "🌮", "🍟", "🥤"],    # Food theme
    ["🍺", "🥃", "🍷", "🥂", "🍸"]     # Drink theme
]

# ==============================
# NAME GENERATOR - 10,000+ combinations
# ==============================
NAME_PREFIXES = [
    "Moon", "Space", "Stellar", "Cosmic", "Galactic", "Star", "Rocket",  # Space
    "Doge", "Shiba", "Floki", "Akita", "Corgi", "Puppy", "Wolf",         # Dogs
    "Cat", "Kitty", "Neko", "Feline", "Tiger", "Lion", "Panther",        # Cats
    "Pepe", "Frog", "Toad", "Kek", "Ribbit",                             # Frogs
    "King", "Queen", "Prince", "Lord", "Emperor", "Master", "Boss",      # Royalty
    "Elon", "Musk", "Bezos", "Satoshi", "Vitalik", "Chad", "Gigachad",   # People
    "Ape", "Gorilla", "Monkey", "Baboon", "Chimp", "Orangutan",          # Apes
    "Baby", "Mini", "Little", "Micro", "Tiny", "Mega", "Ultra", "Super", # Size
    "Pixel", "Bit", "Crypto", "Block", "Chain", "Coin", "Token",         # Crypto
    "Gold", "Silver", "Diamond", "Emerald", "Ruby", "Platinum", "Gem",   # Valuable
    "Fire", "Flame", "Blaze", "Burn", "Inferno", "Phoenix",              # Fire
    "Ice", "Frost", "Frozen", "Snow", "Glacier", "Winter",               # Ice
    "Thunder", "Lightning", "Storm", "Tempest", "Hurricane",             # Weather
    "Dragon", "Wyvern", "Hydra", "Basilisk", "Serpent",                  # Mythical creatures
    "Ninja", "Samurai", "Warrior", "Knight", "Viking", "Pirate",         # Warriors
    "Ghost", "Spirit", "Phantom", "Shadow", "Specter", "Wraith",         # Spectral
    "Magic", "Wizard", "Sorcerer", "Mage", "Enchanter", "Mystic",        # Magic
    "Robot", "Cyborg", "Android", "Mech", "Machine", "AI",               # Robots
    "Alien", "Martian", "UFO", "ET", "Xenomorph", "Predator",            # Aliens
    "Pizza", "Burger", "Taco", "Sushi", "Donut", "Sandwich"              # Food
]

NAME_SUFFIXES = [
    "Moon", "Mars", "Star", "Comet", "Galaxy", "Nova", "Nebula",         # Space
    "Coin", "Token", "Cash", "Money", "Dollar", "Cent", "Credit",        # Money
    "Doge", "Inu", "Shiba", "Akita", "Floki", "Puppy", "Pup",            # Dogs
    "Cat", "Kitten", "Kitty", "Neko", "Feline", "Tabby",                 # Cats
    "Frog", "Toad", "Pepe", "Kek", "Ribbit",                             # Frogs
    "King", "Queen", "Lord", "Emperor", "Royalty", "Monarch",            # Royalty
    "Rocket", "Shuttle", "Ship", "Jet", "Missile",                       # Vehicles
    "Ape", "Gorilla", "Kong", "Chimp", "Monkey",                         # Apes
    "Bit", "Byte", "Crypto", "Chain", "Net", "Web", "Protocol",          # Tech
    "Diamond", "Gold", "Silver", "Platinum", "Emerald", "Ruby",          # Valuable
    "Fire", "Flame", "Blaze", "Inferno", "Heat",                         # Fire
    "Ice", "Frost", "Snow", "Glacier", "Freeze",                         # Ice
    "Bolt", "Shock", "Thunder", "Lightning", "Storm",                    # Weather
    "Dragon", "Wyvern", "Hydra", "Beast", "Monster",                     # Creatures
    "Ninja", "Samurai", "Warrior", "Knight", "Hero",                     # Warriors
    "Ghost", "Spirit", "Phantom", "Shadow", "Specter",                   # Spectral
    "Wizard", "Mage", "Sorcerer", "Warlock", "Mystic",                   # Magic
    "Bot", "Droid", "Robot", "Mech", "Machine",                          # Robots
    "Finance", "DeFi", "Swap", "Exchange", "Trade", "Market",            # Finance
    "X", "Z", "Plus", "Pro", "Ultra", "Max", "Elite", "Premium"          # Modifiers
]

def generate_memecoin_name():
    """Generate a random memecoin name"""
    # 80% chance for prefix + suffix
    if random.random() < 0.8:
        prefix = random.choice(NAME_PREFIXES)
        suffix = random.choice(NAME_SUFFIXES)
        # Avoid duplicates like MoonMoon
        while prefix == suffix:
            suffix = random.choice(NAME_SUFFIXES)
        name = prefix + suffix
    # 20% chance for solo name with modifier
    else:
        main_word = random.choice(NAME_PREFIXES + NAME_SUFFIXES)
        # 50% chance to add a year
        if random.random() < 0.5:
            import datetime
            year = datetime.datetime.now().year
            name = f"{main_word}{year}"
        # 50% chance to add special formatting
        else:
            format_choice = random.randint(1, 4)
            if format_choice == 1:
                name = f"{main_word}X"  # e.g., DogeX
            elif format_choice == 2:
                name = f"x{main_word}"  # e.g., xDoge
            elif format_choice == 3:
                name = f"{main_word}DAO"  # e.g., DogeDAO
            else:
                name = f"{main_word.upper()}"  # e.g., DOGE
    
    return name

# ==============================
# SYMBOL GENERATOR
# ==============================
def generate_symbol(name):
    """Generate a token symbol from the name"""
    # 40% chance: use first letters of compound names
    if random.random() < 0.4 and len(name) > 3:
        # Find capital letters in the name (indicating compound word)
        capitals = [c for c in name if c.isupper()]
        if len(capitals) >= 2:
            symbol = ''.join(capitals)
            if len(symbol) > 5:  # Trim if too long
                symbol = symbol[:5]
            return symbol
    
    # 30% chance: use first 3-4 letters
    if random.random() < 0.7:
        symbol_length = random.randint(3, 4)
        symbol = name[:symbol_length].upper()
        return symbol
    
    # 30% chance: create symbol with $ prefix
    prefix = random.choice(["$", ""])
    
    # Get first 2-4 characters
    length = min(len(name), random.randint(2, 4))
    base_symbol = name[:length].upper()
    
    return f"{prefix}{base_symbol}"

# ==============================
# WEBSITE GENERATOR FUNCTION
# ==============================
def generate_unique_website_data(coin_name=None):
    """Generate a completely unique website configuration"""
    # Generate a memecoin name if not provided
    if not coin_name:
        coin_name = generate_memecoin_name()
    
    # Generate a symbol based on the name
    symbol = generate_symbol(coin_name)
    
    # Format coin name for display (e.g., FlokiElon -> Floki Elon)
    formatted_name = ' '.join(re.findall(r'[A-Z][a-z]*', coin_name))
    if not formatted_name:
        formatted_name = coin_name
    
    # Pick random theme
    theme = random.choice(THEMES)
    
    # Generate a slogan
    slogan = get_random_slogan()
    
    # Generate tokenomics
    tokenomic = generate_tokenomics()
    
    # Generate roadmap
    roadmap = generate_roadmap()
    
    # Pick emoji set
    emoji_set = random.choice(EMOJI_SETS)
    
    # Create website data
    website_data = {
        "name": coin_name,
        "formatted_name": formatted_name,
        "symbol": symbol,
        "slogan": slogan,
        "tokenomics": tokenomic,
        "roadmap": roadmap[0],  # Just use phase 1 for now
        "theme": {
            "primary": theme["primary"],
            "secondary": theme["secondary"],
            "accent": theme["accent"],
            "name": theme["name"]
        },
        "emojis": emoji_set,
        "show_tokenomics": True  # Default to showing tokenomics
    }
    
    return website_data


# If this file is run directly, demonstrate some example generations
if __name__ == "__main__":
    for _ in range(5):
        data = generate_unique_website_data()
        print(f"Name: {data['name']} ({data['symbol']})")
        print(f"Slogan: {data['slogan']}")
        print(f"Theme: {data['theme']['name']}")
        print(f"Tokenomics: Total Supply: {data['tokenomics']['total_supply']}")
        print(f"Roadmap Items: {', '.join(data['roadmap'])}")
        print("-" * 50)