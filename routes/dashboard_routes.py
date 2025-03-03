from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import db
from models import User, Deck

class Dashboard(Resource):
    @jwt_required()
    def get(self):
        """
        Fetches the logged-in user's dashboard data, including:
        - Total flashcards studied
        - Most reviewed decks
        - Overall progress tracking
        - Study statistics (weekly goal, mastery level, streak, focus, retention, minutes per day)
        """
        user_data = get_jwt_identity()
        user_id = user_data.get("id")
        
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {"error": "User not found"}, 404
        
        # Fetch user's decks
        decks = Deck.query.filter_by(user_id=user_id).all()
        deck_data = []
        total_flashcards_studied = 0
        most_reviewed_deck = None
        most_reviews = 0
        
        for deck in decks:
            progress_entries = Progress.query.filter_by(deck_id=deck.id, user_id=user_id).all()
            deck_study_count = sum(entry.study_count for entry in progress_entries)
            total_flashcards_studied += deck_study_count

            # Track the most reviewed deck
            if deck_study_count > most_reviews:
                most_reviews = deck_study_count
                most_reviewed_deck = deck.title

            deck_data.append({
                "deck_id": deck.id,
                "deck_title": deck.title,
                "flashcards_studied": deck_study_count
            })

        # Fetch user stats
        stats = UserStats.query.filter_by(user_id=user_id).first()
        if not stats:
            stats = UserStats(user_id=user_id)
            db.session.add(stats)
            db.session.commit()
        
        # Compute mastery level (accuracy %)
        total_correct = db.session.query(db.func.sum(Progress.correct_attempts)).filter_by(user_id=user_id).scalar() or 0
        total_attempts = db.session.query(db.func.sum(Progress.study_count)).filter_by(user_id=user_id).scalar() or 1
        mastery_level = (total_correct / total_attempts) * 100 if total_attempts > 0 else 0

        # Compute retention rate
        retention_rate = mastery_level  # Retention rate is the same as mastery level in this case

        # Compute focus score
        total_study_time = db.session.query(db.func.sum(Progress.total_study_time)).filter_by(user_id=user_id).scalar() or 0
        target_time_per_flashcard = 1  # Target time in minutes per flashcard
        focus_score = 0

        if total_flashcards_studied > 0:
            average_time_per_flashcard = total_study_time / total_flashcards_studied
            focus_score = (average_time_per_flashcard / target_time_per_flashcard) * 100

        # Update user stats with calculated metrics
        stats.mastery_level = mastery_level
        stats.retention_rate = retention_rate
        stats.focus_score = focus_score
        db.session.commit()

        response_data = {
            "username": user.username,
            "total_flashcards_studied": total_flashcards_studied,
            "most    
        
        