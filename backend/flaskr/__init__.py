import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def retrieve_categories():
        try:
            categories = Category.query.order_by(Category.type).all()
            result = {category.id: category.type for category in categories}

            if len(categories) == 0:
                abort(404)

            return jsonify({
                'categories': result
                })
        except Exception as e:
            abort(422)

    @app.route('/questions')
    def retrieve_questions():
        try:
            page = request.args.get('page', 1, type=int)
            current_index = page-1

            questionCount = Question.query.count()
            questions = Question.query.order_by(Question.id)\
                .limit(QUESTIONS_PER_PAGE)\
                .offset(current_index * QUESTIONS_PER_PAGE).all()
            categories = Category.query.order_by(Category.type).all()

            if len(questions) == 0:
                abort(404)

            return jsonify({
                'questions': [question.format() for question in questions],
                'total_questions': questionCount,
                'categories': {
                    category.id: category.type for category in categories
                    },
                'current_category': categories[0].type
            })
        except Exception as e:
            abort(422)

    @app.route("/categories/<categoryId>/questions")
    def getQuestionsByCategory(categoryId):
        try:
            questions = Question.query.filter(Question.category == categoryId)\
                .all()
            category = Category.query.get(categoryId)

            if not category:
                abort(404)
            if len(questions) == 0:
                abort(404)
            print("return")
            return jsonify({
                'questions': [question.format() for question in questions],
                'totalQuestions': len(questions),
                'currentCategory': category.type
                })
        except Exception as e:
            print(sys.exc_info())
            abort(422)

    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)

            if not question:
                abort(404)

            question.delete()
            return jsonify({
                # 'success': True,
                'deleted': question_id
            })
        except Exception as e:
            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()
            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)

            category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')

            if category['type'] == 'click':
                questions = Question.query.filter(
                    Question.id.notin_((previous_questions))).all()
            else:
                questions = Question.query.filter_by(
                    category=category['id']).filter(
                        Question.id.notin_((previous_questions))).all()

            if len(questions) < 1:
                abort(404)

            question = questions[random.randrange(0, len(questions))]

            return jsonify({
                'success': True,
                'question': question.format()
            })
        except Exception as e:
            print(sys.exc_info())
            abort(422)

    @app.route("/questions", methods=['POST'])
    def add_question():

        body = request.get_json()

        if 'question' not in body or 'answer' not in body\
                or 'difficulty' not in body or 'category' not in body:
            abort(422)

        try:
            question = Question(question=body.get('question'),
                                answer=body.get('answer'),
                                difficulty=body.get('difficulty'),
                                category=body.get('category'))
            question.insert()

            return jsonify({
                # 'success': True,
                'created': question.id,
            })

        except Exception as e:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            body = request.get_json()
            search_term = body.get('searchTerm', None)
            print(search_term)

            if search_term:
                result = Question.query.filter(
                    Question.question.ilike(f'%{search_term}%')).all()

                return jsonify({
                    'questions': [question.format() for question in result],
                    'total_questions': len(result),
                    'current_category': None
                })
            else:
                abort(404)
        except Exception as e:
            print(sys.exc_info())
            abort(422)

    @app.route('/categories/<category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):
        try:
            questions = Question.query.filter(
                Question.category == str(category_id)).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': questions[0].category
            })
        except Exception as e:
            abort(404)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    return app
