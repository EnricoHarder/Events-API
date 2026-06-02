from flask import Blueprint, request, jsonify
from models import db, Poll, PollOption
from flask_jwt_extended import jwt_required, get_jwt_identity

polls_bp = Blueprint('polls', __name__, url_prefix='/api/polls')

@polls_bp.route('', methods=['POST'])
@jwt_required()
def create_poll():
    """Create a new poll (requires authentication)"""
    data = request.get_json()
    
    if not data or not data.get('question') or not data.get('options'):
        return jsonify({'error': 'Question and options are required'}), 400
    
    user_id = int(get_jwt_identity())
    
    poll = Poll(
        question=data['question'],
        is_public=data.get('is_public', True),
        requires_admin=data.get('requires_admin', False),
        created_by=user_id
    )
    
    db.session.add(poll)
    db.session.commit()
    
    for option_text in data['options']:
        option = PollOption(text=option_text, poll_id=poll.id)
        db.session.add(option)
    
    db.session.commit()
    
    return jsonify(poll.to_dict()), 201