import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        database_user = "postgres"
        database_pass = "postgres"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            database_user, database_pass, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            # self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass


    def test_getCategories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['categories'])


    def test_getQuestions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertIsNotNone(data['questions'])

    def test_getQuestionsByCategory(self):
        res = self.client().get('/categories/5/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertIsNotNone(data['totalQuestions'])
        self.assertIsNotNone(data['currentCategory'])

    def test_addQuestion(self):
        question = {
            'question': 'testQuestion',
            'answer': 'testAnswer',
            'difficulty': 1,
            'category': 1
        }

        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)

        question = Question.query.filter(
            Question.question == 'testQuestion').one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(question.question , 'testQuestion')
        self.assertEqual(question.answer , 'testAnswer')
        self.assertEqual(question.difficulty , 1)
        self.assertEqual(question.category , 1)

    def test_deleteQuestion(self):
        question = Question.query.filter(
            Question.question == 'testQuestion').one_or_none()
        question_id = question.id

        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == question.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['deleted'], str(question_id))


    def test_search_questions(self):
        search = {'searchTerm': 'heav'}
        res = self.client().post('/questions/search', json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_play_quiz(self):
        query = {'previous_questions': [2,11],
                          'quiz_category': {'type': 'click', 'id': 0}}

        res = self.client().post('/quizzes', json=query)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True )


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
