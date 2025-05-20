"""
Customization API Module for the Website Creator

This module provides API endpoints for the template customization flow.
It ties together the state management, template handling, and website generation.
"""

import os
import logging
import json
import hashlib
from flask import Blueprint, request, jsonify, send_from_directory, render_template
from customization_states import STATES, CustomizationStateManager
from customization_flow import (
    get_or_create_state_manager,
    handle_template_selection,
    handle_coin_name,
    handle_slogan,
    handle_description,
    handle_logo,
    handle_theme,
    handle_color_scheme,
    handle_social_link,
    handle_tokenomics,
    handle_roadmap,
    handle_sections_order,
    handle_confirmation,
    handle_edit_choice,
    generate_website,
    reset_state,
    get_state_summary,
    get_templates,
    get_themes
)
from template_handlers import TemplateManager

# Configure logging
logging.basicConfig(
    filename='flask_app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Create blueprint
customization_bp = Blueprint('customization', __name__)

# Initialize template manager
template_manager = TemplateManager()

# API endpoints
@customization_bp.route('/api/templates', methods=['GET'])
def api_get_templates():
    """API endpoint to get available templates."""
    templates = get_templates()
    return jsonify({"templates": templates})

@customization_bp.route('/api/themes', methods=['GET'])
def api_get_themes():
    """API endpoint to get available themes."""
    themes = get_themes()
    return jsonify({"themes": themes})

@customization_bp.route('/api/state', methods=['GET'])
def api_get_state():
    """API endpoint to get the current state for a user."""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400
    
    state_summary = get_state_summary(user_id)
    return jsonify(state_summary)

@customization_bp.route('/api/state/reset', methods=['POST'])
def api_reset_state():
    """API endpoint to reset the state for a user."""
    data = request.json
    
    if not data or 'user_id' not in data:
        return jsonify({"error": "Missing user_id parameter"}), 400
    
    user_id = data['user_id']
    result = reset_state(user_id)
    return jsonify(result)

@customization_bp.route('/api/template/select', methods=['POST'])
def api_select_template():
    """API endpoint to select a template."""
    data = request.json
    
    if not data or 'user_id' not in data or 'template_id' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    user_id = data['user_id']
    template_id = data['template_id']
    
    result = handle_template_selection(user_id, template_id)
    return jsonify(result)

@customization_bp.route('/api/coin/name', methods=['POST'])
def api_set_coin_name():
    """API endpoint to set the coin name."""
    data = request.json
    
    if not data or 'user_id' not in data or 'coin_name' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    user_id = data['user_id']
    coin_name = data['coin_name']
    
    result = handle_coin_name(user_id, coin_name)
    return jsonify(result)

@customization_bp.route('/api/coin/slogan', methods=['POST'])
def api_set_slogan():
    """API endpoint to set the coin slogan."""
    data = request.json
    
    if not data or 'user_id' not in data or 'slogan' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    user_id = data['user_id']
    slogan = data['slogan']
    
    result = handle_slogan(user_id, slogan)
    return jsonify(result)

@customization_bp.route('/api/coin/description', methods=['POST'])
def api_set_description():
    """API endpoint to set the coin description."""
    data = request.json
    
    if not data or 'user_id' not in data or 'description' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    user_id = data['user_id']
    description = data['description']
    
    result = handle_description(user_id, description)
    return jsonify(result)

@customization_bp.route('/api/coin/logo', methods=['POST'])
def api_set_logo():
    """API endpoint to set the coin logo."""
    # Handle both form data (file upload) and JSON
    user_id = request.form.get('user_id') if request.form else request.json.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400
    
    # Check if a file was uploaded
    logo_file = request.files.get('logo_file')
    logo_url = request.form.get('logo_url') if request.form else request.json.get('logo_url')
    
    result = handle_logo(user_id, logo_url, logo_file)
    return jsonify(result)

@customization_bp.route('/api/theme', methods=['POST'])
def api_set_theme():
    """API endpoint to set the website theme."""
    data = request.json
    
    if not data or 'user_id' not in data or 'theme_id' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    user_id = data['user_id']
    theme_id = data['theme_id']
    
    result = handle_theme(user_id, theme_id)
    return jsonify(result)

@customization_bp.route('/api/colors', methods=['POST'])
def api_set_colors():
    """API endpoint to set the color scheme."""
    data = request.json
    
    if not data or 'user_id' not in data or 'colors' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    user_id = data['user_id']
    colors = data['colors']
    
    result = handle_color_scheme(user_id, colors)
    return jsonify(result)

@customization_bp.route('/api/social', methods=['POST'])
def api_set_social():
    """API endpoint to set a social media link."""
    data = request.json
    
    if not data or 'user_id' not in data or 'platform' not in data or 'url' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    user_id = data['user_id']
    platform = data['platform']
    url = data['url']
    
    result = handle_social_link(user_id, platform, url)
    return jsonify(result)

@customization_bp.route('/api/tokenomics', methods=['POST'])
def api_set_tokenomics():
    """API endpoint to set tokenomics information."""
    data = request.json
    
    if not data or 'user_id' not in data or 'field' not in data or 'value' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    user_id = data['user_id']
    field = data['field']
    value = data['value']
    
    result = handle_tokenomics(user_id, field, value)
    return jsonify(result)

@customization_bp.route('/api/roadmap', methods=['POST'])
def api_set_roadmap():
    """API endpoint to set the roadmap."""
    data = request.json
    
    if not data or 'user_id' not in data or 'roadmap' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    user_id = data['user_id']
    roadmap = data['roadmap']
    
    result = handle_roadmap(user_id, roadmap)
    return jsonify(result)

@customization_bp.route('/api/sections', methods=['POST'])
def api_set_sections():
    """API endpoint to set the sections order."""
    data = request.json
    
    if not data or 'user_id' not in data or 'sections_order' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    user_id = data['user_id']
    sections_order = data['sections_order']
    
    result = handle_sections_order(user_id, sections_order)
    return jsonify(result)

@customization_bp.route('/api/confirm', methods=['POST'])
def api_confirm():
    """API endpoint to confirm the website details."""
    data = request.json
    
    if not data or 'user_id' not in data or 'confirmed' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    user_id = data['user_id']
    confirmed = data['confirmed']
    
    result = handle_confirmation(user_id, confirmed)
    return jsonify(result)

@customization_bp.route('/api/edit', methods=['POST'])
def api_edit_choice():
    """API endpoint to select a field to edit."""
    data = request.json
    
    if not data or 'user_id' not in data or 'field' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    user_id = data['user_id']
    field = data['field']
    
    result = handle_edit_choice(user_id, field)
    return jsonify(result)

@customization_bp.route('/api/generate', methods=['POST'])
def api_generate_website():
    """API endpoint to generate the website."""
    data = request.json
    
    if not data or 'user_id' not in data:
        return jsonify({"error": "Missing user_id parameter"}), 400
    
    user_id = data['user_id']
    
    result = generate_website(user_id)
    return jsonify(result)

# Direct template customization endpoint - combines all steps for quick generation
@customization_bp.route('/api/generate/direct', methods=['POST'])
def api_generate_direct():
    """
    API endpoint to directly generate a website without going through the state flow.
    This is useful for integrations or batch operations.
    """
    data = request.json
    
    if not data or 'template_id' not in data or 'site_hash' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    template_id = data['template_id']
    site_hash = data['site_hash']
    
    try:
        # Validate data against template requirements
        validation = template_manager.validate_template_data(template_id, data)
        
        if not validation['valid']:
            return jsonify({"error": validation['error']}), 400
        
        # Process data for the selected template
        processed_data = template_manager.process_template_data(template_id, data)
        
        # Render the template
        template_path = template_manager.get_template_html_path(template_id)
        template_filename = os.path.basename(template_path)
        
        html_content = render_template(template_filename, **processed_data)
        
        # Save the generated site
        file_path = template_manager.save_generated_site(site_hash, html_content)
        
        return jsonify({
            "status": "success",
            "site_hash": site_hash,
            "file_path": file_path,
            "url": f"/sites/{site_hash}.html"
        })
    
    except Exception as e:
        logger.error(f"Error generating website directly: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Initialize the customization API
def init_app(app):
    """Initialize the Flask app with the customization API."""
    app.register_blueprint(customization_bp)
    
    # Make sure required directories exist
    os.makedirs('sites', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    logger.info("Customization API initialized")