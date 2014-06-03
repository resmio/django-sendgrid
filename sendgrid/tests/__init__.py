import django

import unittest

if django.VERSION[0] == 1 and django.VERSION[1] < 6:
    def suite():
        return unittest.TestLoader().discover("sendgrid.tests", pattern="*.py")
