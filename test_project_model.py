"""User model tests."""

import os
from unittest import TestCase

from models import db, User, Project, Yarn, Needle, Hook, TimeLog

# set up test database before importing app because
# app already connected to a database
os.environ['DATABASE_URL'] = "postgresql:///craft_app_test"

from app import app

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    def setUp(self):
        Project.query.delete()
        User.query.delete()

        u1 = User.signup(
            username="u1",
            email="u1@email.com",
            password='password',
            image_url=None,
        )

        p1 = Project(
            user_id=u1.id,
            title='test_title',
            pattern='test_pattern',
            designer='test_designer',
            content='test_content'
        )

        u1.projects.append(p1)

        db.session.add(u1)
        db.session.commit()

        self.u1_id = u1.id
        self.p1_id = p1.id


    def tearDown(self):
        db.session.rollback()

    def test_project_model(self):
        """Test project instance initialized correctly."""

        p1 = Project.query.get(self.p1_id)

        self.assertIsInstance(p1, Project)
        self.assertEqual(p1.title, 'test_title')
        self.assertEqual(p1.pattern, 'test_pattern')
        self.assertEqual(p1.designer, 'test_designer')
        self.assertEqual(p1.content, 'test_content')
        self.assertEqual(len(p1.yarns), 0)
        self.assertEqual(len(p1.needles), 0)
        self.assertEqual(len(p1.hooks), 0)
        self.assertEqual(len(p1.time_logs), 0)

    # #################### Relationships Tests

    def test_project_yarns(self):
        """Test project to yarn relationship."""

        p1 = Project.query.get(self.p1_id)
        y1 = Yarn(
                yarn_name='test_name',
                color='test_color',
                dye_lot='test_dye_lot',
                weight='test_weight',
                skein_weight=0,
                skein_weight_unit='test_unit',
                skein_length=0,
                skein_length_unit='test_unit',
                num_skeins=0
            )
        p1.yarns.append(y1)
        db.session.commit()

        yarns = Yarn.query.filter(Yarn.project_id == p1.id).all()
        self.assertEqual(len(yarns), 1)
        self.assertEqual(p1.yarns, [y1])
        self.assertEqual(y1.project_id, p1.id)
        self.assertEqual(yarns[0].yarn_name, 'test_name')
        self.assertEqual(yarns[0].color, 'test_color')
        self.assertEqual(yarns[0].dye_lot, 'test_dye_lot')
        self.assertEqual(yarns[0].weight, 'test_weight')
        self.assertEqual(yarns[0].skein_weight, 0)
        self.assertEqual(yarns[0].skein_weight_unit, 'test_unit')
        self.assertEqual(yarns[0].skein_length, 0)
        self.assertEqual(yarns[0].skein_length_unit, 'test_unit')
        self.assertEqual(yarns[0].num_skeins, 0)

    def test_project_needle(self):
        """Test projects to needle relationships."""

        p1 = Project.query.get(self.p1_id)
        n1 = Needle(size='test_size')
        p1.needles.append(n1)
        db.session.commit()

        self.assertEqual(p1.needles, [n1])
        self.assertEqual(n1.projects, [p1])

    def test_project_hook(self):
        """Test projects to hooks relationship."""

        p1 = Project.query.get(self.p1_id)
        h1 = Hook(size='test_size')
        p1.hooks.append(h1)
        db.session.commit()

        self.assertEqual(p1.hooks, [h1])
        self.assertEqual(h1.projects, [p1])

    def test_project_log(self):
        """Test projects to logs relationship."""

        p1 = Project.query.get(self.p1_id)
        l1 = TimeLog(
                date='2024-03-14 21:31:36.079171',
                hours=0,
                minutes=30,
                notes='test_notes'
            )
        p1.time_logs.append(l1)
        db.session.commit()

        logs = TimeLog.query.filter(TimeLog.project_id == p1.id).all()
        self.assertEqual(len(logs), 1)
        self.assertEqual(p1.time_logs, [l1])
        self.assertEqual(l1.project_id, p1.id)
